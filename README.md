# Marathon Analysis

<p align="center">
  <img  src="https://github.com/kmax12/marathon_analysis/blob/main/output/finish_time_vs_percent_slowdown.png">
</p>

**Notebooks for analyzing marathon split and finish times.**

**Read more:** https://www.jmaxkanter.com/posts/chicago-marathon-2022/

## Getting Started

You can recreate the analysis by running the following steps

### 1. Install

```
pip install -r requirements.txt
```

### 2. Scrape Data

A scrapper for the 2021 Chicago Marathon is available in `Scrape Data.ipynb`. Running this notebook will prepare an output file named `all_runners_with_splits.csv`

### 3. Run Analysis

You can run the analyze yourself using `Analyze Data.ipynb`.

## Use your own data

The input format is a CSV file with one runner per row and column for each split. You can see example CSV file [here](https://github.com/kmax12/marathon_analysis/blob/main/sample_data.csv).

## Feedback

If you found this interesting or have ideas on how to improve, please post a GitHub issue or reach out via email! I would love to hear from you
