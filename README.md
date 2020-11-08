# ComPora
A set of scripts to **Com**pile different kind of cor**Pora** easily and quickly.

## Installation
Three different installation methods are shown bellow:

1. Install `CompPora` or `compora` from PyPI:
``` bash
pip install ComPora
```
or
``` bash
pip install compora
```

2. Install `ComPora` from sources:
```bash
git clone https://github.com/Jason-Young-AI/ComPora.git
cd ComPora
python setup.py install
```

3. Develop `ComPora` locally:
```bash
git clone https://github.com/Jason-Young-AI/ComPora.git
cd ComPora
python setup.py build develop
```

## Command Line Interface

Now support:

* [compora-parallel](#compora-parallel)

## Usage

See [Full Documentation](https://jason-young.me/ComPora/) for more details.

### compora-parallel

This script is used to preprocess parallel corpus and support Multi-Process.

It directly integrates several common preprocessing functions which is implemented in the same way as [**MosesDecoder**](https://github.com/moses-smt/mosesdecoder), like `punctuation normalization` ( [normalize-punctuation.perl](https://github.com/moses-smt/mosesdecoder/blob/master/scripts/tokenizer/normalize-punctuation.perl) (without -penn flag) and [replace-unicode-punctuation.perl](https://github.com/moses-smt/mosesdecoder/blob/master/scripts/tokenizer/replace-unicode-punctuation.perl) ), `tokenization` ([tokenizer.perl](https://github.com/moses-smt/mosesdecoder/blob/master/scripts/tokenizer/tokenizer.perl) (without -penn flag) ) and `Character normalization` ( [remove-non-printing-char.perl](https://github.com/moses-smt/mosesdecoder/blob/master/scripts/tokenizer/remove-non-printing-char.perl) ).

It also provides several additional optional functions, such as eliminate abnormal sentence pairs that the ratio of the longest sentence length to the shortest sentence length is too large in the source sentence and the target sentence.

If you have a raw Chinese-English parallel corpus (chinese: `corpus-zh`; english: `corpus-en`), you can compile the corpus like this:
```bash
compora-parallel --number-worker 10 --work-amount 100000 --eliminate-abnormal -r 5.0 -s zh -t en corpus-zh corpus-en corpus-zh-compiled corpus-en-compiled
```

Just run `compora-parallel --help` for more help.
