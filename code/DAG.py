import networkx as nx
import matplotlib.pyplot as plt

# Create a directed graph
G = nx.DiGraph()

# Add edges based on the DAG structure
edges = [
    ("Teacher", "AC_Ind"),
    ("Teacher", "Grades"),
    ("Attendance", "Grades"),
    ("School", "Teacher"),
    ("School", "Grades"),
    ("School", "AC_Ind"),
    ("Disadvantage", "Grades"),
    ("Disadvantage", "Attendance"),
    ("Disadvantage", "AC_Ind"),
    ("Overall_GPA", "AC_Ind")
]

G.add_edges_from(edges)

# Draw the DAG
plt.figure(figsize=(10, 8))
pos = nx.shell_layout(G)  # Trying a shell layout for better separation
nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=3000, font_size=10)
plt.title("DAG for Advanced Coursework ASC Project")
plt.show()
