# Read This First

This work is being done by someone else much better than me. The work here was to simply get somethign janky working for my own purposes. Nebulock is working on this same thing but much more fleshed out. Check out the blog about [coreSigma](https://nebulock.io/blog/coresigma-expanding-sigma-detection-for-macos) first.

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

You can get sigma with `brew install sigma-cli` or with your package manager of choice. 

Make sure if you're running this through elasticsearch, you have your search set to `lucene` not `KQL`.

