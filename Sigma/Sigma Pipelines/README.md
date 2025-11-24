## Caveat

This pipeline was a janky solution for my own research. If you decide to try to use it yourself... for some reason... the usage is as follows:

### Transform your sigma rules to use ECS fields

```
python3 transform_rules.py [input directory or rule file] [output directory or rule file]
```

### Then run these rules using the lucene target and the macos-esf.yaml

```
sigma convert -t lucene -p ./macos-esf.yaml [directory of transformed files, or transformed file]
```

You need to do a `sigma plugin install elasticsearch` to have lucene as an option, you may also need to install missing packages like `pyYAML` using `pip install pyyaml` or `pip3 install pyyaml`. If you're in a virtual environment, `python3 -m pip install pyyaml`.