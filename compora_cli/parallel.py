import os
import re
import sys
import argparse
import functools

from yoolkit.cio import mk_temp, rm_temp, dump_datas, load_datas, load_plain
from yoolkit.text import unicode_category, detect_file_encoding, normalize
from yoolkit.logging import setup_logger, logging_level
from yoolkit.xmlscape import encode, decode
from yoolkit.constant import Constant
from yoolkit.multiprocessing import multi_process

from compora.tokenize import tokenize, split_aggressive_hyphen
from compora.segmenter import Segmenter
from compora.standardize import standardize
from compora.special_process import special_process


constant = Constant()
constant.LANGUAGE_CHOICES = [
    'ca', 'cs', 'de', 'el', 'en', 'es', 'fi', 'fr', 'ga', 'hu',
    'is', 'it', 'lt', 'lv', 'nl', 'pl', 'pt', 'ro', 'ru', 'sk',
    'sl', 'sv', 'ta', 'zh', 'yue',
]


def get_arguments():
    argument_parser = argparse.ArgumentParser(allow_abbrev=True, formatter_class=argparse.RawTextHelpFormatter)
    argument_parser.add_argument(
        'source_input_file_path',
        metavar='SRC-IN',
        help=('The path of source file to be read.\n'),
    )
    argument_parser.add_argument(
        'target_input_file_path',
        metavar='TGT-IN',
        help=('The path of target file to be read.\n'),
    )
    argument_parser.add_argument(
        'source_output_file_path',
        metavar='SRC-OUT',
        help=('The path of compiled source file to be wrote.\n'),
    )
    argument_parser.add_argument(
        'target_output_file_path',
        metavar='TGT-OUT',
        help=('The path of compiled target file to be wrote.\n'),
    )

    argument_parser.add_argument(
        '--lowercase',
        action='store_true',
        help=('Lowercase all chars in the source and target file.\n'),
    )
    argument_parser.add_argument(
        '--no-escape',
        action='store_true',
        help=('Do not escape XML chars in the source and target file.\n'),
    )

    argument_parser.add_argument(
        '--eliminate-abnormal',
        action='store_true',
        help=('Eliminate abnormal sentence pair. If this flag is set, --length-ratio will take effect.\n'),
    )
    argument_parser.add_argument(
        '-r',
        '--length-ratio',
        type=float,
        metavar='N',
        default=5.0,
        help=('Eliminate sentence pair that the length ratio (len(source)/len(target) or len(target)/len(source)) larger than --length-ratio.\n'
              'DEFAULT=5'),
    )

    argument_parser.add_argument(
        '-s',
        '--source-language',
        metavar='SRC-LANG',
        default='en',
        choices=constant.LANGUAGE_CHOICES,
        help=('The language of source file.\n'
              'DEFAULT=\'en\''),
    )
    argument_parser.add_argument(
        '-t',
        '--target-language',
        metavar='TGT-LANG',
        default='en',
        choices=constant.LANGUAGE_CHOICES,
        help=('The language of target file.\n'
              'DEFAULT=\'en\''),
    )

    argument_parser.add_argument(
        '--number-worker',
        type=int,
        metavar='N',
        default=1,
        help=('How many threads you want to use?\n'
              'DEFAULT=1'),
    )

    argument_parser.add_argument(
        '--work-amount',
        type=int,
        metavar='N',
        default=1000000,
        help=('How many lines do you want the thread to process?\n'
              'DEFAULT=1000000'),
    )

    arguments = argument_parser.parse_args()
    return arguments


def remove_control_char(lines):
    inter_path = mk_temp('compora-inter_', temp_type='file')
    with open(inter_path, 'w', encoding='utf-8') as inter_file:
        for line in lines:
            control_chars = ''
            for char in line:
                if 'C' in unicode_category(char):
                    control_chars += char
                else:
                    continue

            if len(control_chars) != 0:
                line = re.sub(rf'([{control_chars}])', ' ', line)
            inter_file.writelines(line + '\n')
    return inter_path


def merge(inter_paths, logger):
    temp_path = mk_temp('compora-temp_', temp_type='file')
    with open(temp_path, 'w', encoding='utf-8') as temp_file:
        for index, inter_path in enumerate(inter_paths):
            logger.info(f'   Writing {index}/{len(inter_paths)} part of corpus ...')
            with open(inter_path, 'r', encoding='utf-8', newline='\n') as inter_file:
                for line in inter_file:
                    temp_file.writelines(line)
            rm_temp(inter_path)
    return temp_path


def compile_sentence(
        paired_lines, source_language, target_language,
        source_segmenter, target_segmenter, lowercase, no_escape,
    ):
    inter_compiled_path = mk_temp('compora-inter-compiled_', temp_type='file')

    def compiled_sentence():
        s_lines, t_lines = paired_lines
        for index, (s_line, t_line) in enumerate(zip(s_lines, t_lines)):
            # There is no '\n' after text normalization
            s_line = normalize(s_line)
            t_line = normalize(t_line)
            if lowercase:
                s_line = s_line.lower()
                t_line = t_line.lower()
            if min(len(s_line), len(t_line)) == 0:
                continue

            s_line = standardize(s_line, source_language)
            t_line = standardize(t_line, target_language)

            s_line = special_process(s_line, source_language)
            t_line = special_process(t_line, target_language)

            if no_escape:
                pass
            else:
                s_line = encode(s_line)
                t_line = encode(t_line)

            s_line = tokenize(s_line, source_language)
            t_line = tokenize(t_line, target_language)

            s_line = source_segmenter.cut(s_line)
            t_line = target_segmenter.cut(t_line)

            s_line = split_aggressive_hyphen(s_line)
            t_line = split_aggressive_hyphen(t_line)

            if no_escape:
                pass
            else:
                s_line = decode(s_line)
                t_line = decode(t_line)

            if (index + 1) % 10000 == 0:
                print('.', end='')
                sys.stdout.flush()
            yield (s_line, t_line)

        print(f'   ...Process-{os.getpid()} Finished...   \n', end='')

    dump_datas(inter_compiled_path, compiled_sentence())

    return inter_compiled_path


def eliminate_abnormal_sentence_pairs(sentence_pairs, length_ratio):
    for s_line, t_line in sentence_pairs:
        s_list = s_line.split()
        t_list = t_line.split()

        s_len = len(s_list)
        t_len = len(t_list)
        max_len = max(s_len, t_len)
        min_len = min(s_len, t_len)
        if max_len/min_len > length_ratio:
            continue
        yield (s_line, t_line)


def main():
    arguments = get_arguments()
    s_i_path = arguments.source_input_file_path
    t_i_path = arguments.target_input_file_path

    s_o_path = arguments.source_output_file_path
    t_o_path = arguments.target_output_file_path

    s_lang = arguments.source_language
    t_lang = arguments.target_language

    assert arguments.length_ratio > 0, f'--length-ratio <= 1! You do not want to eliminate all the sentences, do you?'

    s_segmenter = Segmenter(s_lang)
    t_segmenter = Segmenter(t_lang)

    logger = setup_logger('compora', logging_level=logging_level['INFO'], to_console=True, to_file=False)

    logger.info(f'Source: {s_i_path}')
    logger.info(f'Target: {s_i_path}')

    logger.info(f'1. Detecting file encoding ...')
    logger.info(f' * source file ...')
    s_enc = detect_file_encoding(s_i_path, detect_times=5000)
    logger.info(f'   encoding is \'{s_enc}\'.')

    logger.info(f' * target file ...')
    t_enc = detect_file_encoding(t_i_path, detect_times=5000)
    logger.info(f'   encoding is \'{t_enc}\'.')

    work_amount = arguments.work_amount
    number_worker = arguments.number_worker
    lowercase = arguments.lowercase
    no_escape = arguments.no_escape

    logger.info(f'2. Removing control chars ...')

    logger.info(f' * source file ...')
    s_partitions = load_plain(s_i_path, file_encoding=s_enc, newline='\n', partition_unit='line', partition_size=work_amount)
    inter_s_paths = multi_process(remove_control_char, s_partitions, number_worker)
    temp_s_path = merge(inter_s_paths, logger)
    logger.info(f'   Finished.')

    logger.info(f' * target file ...')
    t_partitions = load_plain(t_i_path, file_encoding=t_enc, newline='\n', partition_unit='line', partition_size=work_amount)
    inter_t_paths = multi_process(remove_control_char, t_partitions, number_worker)
    temp_t_path = merge(inter_t_paths, logger)
    logger.info(f'   Finished.')

    temp_s_partitions = load_plain(temp_s_path, partition_unit='line', partition_size=work_amount)
    temp_t_partitions = load_plain(temp_t_path, partition_unit='line', partition_size=work_amount)
    temp_partitions = zip(temp_s_partitions, temp_t_partitions)

    logger.info(f'3. Compiling parallel corpus ...')
    partial_compile_sentence = functools.partial(
        compile_sentence,
        source_language=s_lang,
        target_language=t_lang,
        source_segmenter=s_segmenter,
        target_segmenter=t_segmenter,
        lowercase=lowercase,
        no_escape=no_escape,
    )
    inter_compiled_paths = multi_process(partial_compile_sentence, temp_partitions, number_worker)

    rm_temp(temp_s_path)
    rm_temp(temp_t_path)
    logger.info(f'   Finished.')

    logger.info(f'4. Writing the results ...')
    with open(s_o_path, 'w', encoding='utf-8') as sof, open(t_o_path, 'w', encoding='utf-8') as tof:
        for index, inter_compiled_path in enumerate(inter_compiled_paths):
            compiled_sentence = load_datas(inter_compiled_path)
            logger.info(f'   Writing {index}/{len(inter_compiled_paths)} part of corpus ...')
            if arguments.eliminate_abnormal:
                compiled_sentence = eliminate_abnormal_sentence_pairs(
                    compiled_sentence, 
                    length_ratio=arguments.length_ratio,
                )
            for src_line, tgt_line in compiled_sentence:
                sof.writelines(src_line + '\n')
                tof.writelines(tgt_line + '\n')
            rm_temp(inter_compiled_path)
    logger.info(f' $ Complete!')


if __name__ == '__main__':
    main()
