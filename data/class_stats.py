import pandas as pd

classes = pd.read_csv("classes.csv")

excerpts = pd.read_csv("labeled_excerpts.csv")

classes["frequency"] = excerpts.groupby("class_id")["excerpt"].count()

# print(classes)
# print(classes["frequency"].sort_values(reverse=True))

classes.to_csv("classes_with_frequency.csv")