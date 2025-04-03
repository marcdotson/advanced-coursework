# Create a KDE density plot using histogram for AC and Non-AC Students
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import gaussian_kde

# Show plot

warnings.filterwarnings("ignore")

# Load the data from a CSV files
data = pd.read_csv("../data/exploratory_data.csv")
modeldata = pd.read_csv("../data/modeling_data.csv")


import plotly.express as px
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

# Load the data
data = pd.read_csv("../data/exploratory_data.csv")

# Create a Violin plot to compare GPA distributions for AC vs Non-AC Students
fig = px.violin(data, x="ac_ind", y="overall_gpa", color="ac_ind", 
                box=True,  # Add box plot inside the violin plot for clarity
                points="all",  # Show individual points for better visibility
                color_discrete_map={1: "royalblue", 0: "tomato"},
                title="GPA Distributions: AC vs Non-AC Students",
                labels={"ac_ind": "Student Group", "overall_gpa": "Overall GPA"})

# Set the layout for better visual appeal
fig.update_layout(
    template="plotly_white",  # Clean white background
    title_x=0.5,  # Center the title
    xaxis_title="Student Group",
    yaxis_title="Overall GPA",
    showlegend=False,  # Hide legend for simplicity
    xaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=["Non-AC", "AC"]),
    violingap=0.3  # Increase the gap between the two violins
)

# Show plot
fig.show()


fig = px.histogram(data, x="overall_gpa", 
                   histnorm="density", 
                   opacity=0.5, 
                   marginal="rug", 
                   color="ac_ind", 
                   color_discrete_map={1: "blue", 0: "red"},
                   title="Density Plot of Overall GPA: AC and Non-AC Students",
                   nbins=10000000)

# Set x-axis limits
fig.update_xaxes(range=[0, 4])
fig.update_layout(showlegend=True)

# Show plot
fig.show()