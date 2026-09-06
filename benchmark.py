import time
import timeit
from src.nlp.experience_analyzer import ExperienceAnalyzer

text = """
I worked at Google from Jan 2020 - Dec 2022.
Then I worked at Meta from Jan 2023 - Present.
Before that, internship from 05/2018 to 08/2019.
Some other text here with dates 2010 - 2014 and 2015 - 2019.
"""

analyzer = ExperienceAnalyzer()

def run_benchmark():
    for _ in range(10000):
        analyzer._extract_date_intervals(text)

start = time.time()
run_benchmark()
end = time.time()

print(f"Time taken for 10000 iterations: {end - start:.4f} seconds")
