import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
import re

# Set the seaborn style for better visuals
sns.set(style="whitegrid")

# Function to load and prepare data
def load_data(filepath='../data/modeling_data.csv'):
    """Load and prepare the modeling data"""
    df = pd.read_csv(filepath)
    return df

# Function to categorize columns
def categorize_columns(columns):
    """Group columns into meaningful categories"""
    categories = {
        'Academic': [],
        'Demographic': [],
        'Assessment': [],
        'School Status': [],
        'Teacher': [],
        'School': [],
        'Other': []
    }
    
    for col in columns:
        if col == 'student_number':
            continue
        elif col in ['ac_ind', 'overall_gpa', 'percent_days_attended', 'hs_advanced_math_y']:
            categories['Academic'].append(col)
        elif col in ['composite_score', 'english_score', 'math_score', 'reading_score', 'science_score', 'writing_score']:
            categories['Assessment'].append(col)
        elif col.startswith('teacher_'):
            categories['Teacher'].append(col)
        elif col.startswith('school_'):
            categories['School'].append(col)
        elif col.startswith('exit_code_'):
            categories['School Status'].append(col)
        elif col in ['scram_membership', 'environment_h', 'environment_r']:
            categories['School Status'].append(col)
        elif col.startswith(('gender_', 'ethnicity_', 'amerindian_', 'asian_', 'black_', 'hawaiian_', 'white_', 
                           'migrant_', 'military_', 'refugee_', 'homeless_', 'immigrant_', 'tribal_affiliation_')):
            categories['Demographic'].append(col)
        else:
            categories['Other'].append(col)
    
    return categories

# Function to create a correlation heatmap for a feature group
def plot_correlation_heatmap(df, feature_group, group_name):
    """Create a correlation heatmap for a feature group"""
    # Select only numeric columns
    numeric_cols = df[feature_group].select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) < 2:
        return None, f"Not enough numeric features in {group_name} group for correlation analysis"
    
    # Calculate correlation matrix
    corr_matrix = df[numeric_cols].corr()
    
    # Create figure
    plt.figure(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    
    # Generate heatmap
    heatmap = sns.heatmap(
        corr_matrix, 
        mask=mask,
        annot=True, 
        fmt=".2f", 
        cmap="coolwarm",
        vmin=-1, 
        vmax=1, 
        linewidths=0.5
    )
    
    # Set title and labels
    plt.title(f'{group_name} Features - Correlation Matrix', fontsize=16, pad=20)
    plt.tight_layout()
    
    return plt.gcf(), None

# Function to create a distribution plot for a feature group
def plot_feature_distributions(df, feature_group, group_name):
    """Create distribution plots for features in a group"""
    # Select only numeric columns
    numeric_cols = df[feature_group].select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) == 0:
        return None, f"No numeric features in {group_name} group for distribution analysis"
    
    # Limit to 10 features maximum
    if len(numeric_cols) > 10:
        numeric_cols = numeric_cols[:10]
    
    # Create subplots
    n_cols = min(2, len(numeric_cols))
    n_rows = int(np.ceil(len(numeric_cols) / n_cols))
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, n_rows * 4))
    axes = axes.flatten() if isinstance(axes, np.ndarray) else [axes]
    
    # Plot distributions
    for i, col in enumerate(numeric_cols):
        if i < len(axes):
            # Get clean feature name
            feature_name = col.replace('_', ' ').title()
            
            # Plot distribution
            sns.histplot(df[col].dropna(), kde=True, ax=axes[i], color='skyblue')
            axes[i].set_title(feature_name, fontsize=12)
            axes[i].set_xlabel('')
    
    # Hide unused subplots
    for j in range(len(numeric_cols), len(axes)):
        axes[j].set_visible(False)
    
    plt.suptitle(f'{group_name} Features - Distributions', fontsize=16, y=1.02)
    plt.tight_layout()
    
    return fig, None

# Function to create a categorical feature bar plot
def plot_categorical_features(df, feature_group, group_name):
    """Create bar plots for categorical features in a group"""
    # Select categorical columns (binary and categorical)
    cat_cols = df[feature_group].select_dtypes(include=['object', 'bool']).columns.tolist()
    # Add binary numeric columns (usually 0/1 encoded)
    for col in df[feature_group].select_dtypes(include=['number']).columns:
        if df[col].nunique() <= 5:  # Assuming small number of unique values means categorical
            cat_cols.append(col)
    
    if len(cat_cols) == 0:
        return None, f"No categorical features in {group_name} group for bar plot analysis"
    
    # Limit to 9 features maximum
    if len(cat_cols) > 9:
        cat_cols = cat_cols[:9]
    
    # Create subplots
    n_cols = min(3, len(cat_cols))
    n_rows = int(np.ceil(len(cat_cols) / n_cols))
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, n_rows * 4))
    axes = axes.flatten() if isinstance(axes, np.ndarray) else [axes]
    
    # Plot bar charts
    for i, col in enumerate(cat_cols):
        if i < len(axes):
            # Get clean feature name
            feature_name = col.replace('_', ' ').title()
            
            # Plot count of each category
            value_counts = df[col].value_counts().sort_index()
            sns.barplot(x=value_counts.index.astype(str), y=value_counts.values, ax=axes[i], palette='viridis')
            
            # Format the plot
            axes[i].set_title(feature_name, fontsize=12)
            axes[i].set_xlabel('')
            
            # Rotate x-axis labels if there are many categories
            if len(value_counts) > 3:
                axes[i].set_xticklabels(axes[i].get_xticklabels(), rotation=45, ha='right')
    
    # Hide unused subplots
    for j in range(len(cat_cols), len(axes)):
        axes[j].set_visible(False)
    
    plt.suptitle(f'{group_name} Features - Category Distributions', fontsize=16, y=1.02)
    plt.tight_layout()
    
    return fig, None

# Function for creating feature importance plot if you have a trained model
def plot_feature_importance(feature_importance_df, group_name, n_top=10):
    """Create a bar plot of feature importances for a feature group"""
    # Filter for the specific group
    group_importance = feature_importance_df[feature_importance_df['Group'] == group_name]
    
    if len(group_importance) == 0:
        return None, f"No features from {group_name} group in importance data"
    
    # Get top n features
    top_features = group_importance.nlargest(n_top, 'Importance')
    
    # Create figure
    plt.figure(figsize=(10, 6))
    
    # Create bar plot
    bars = sns.barplot(x='Importance', y='Feature', data=top_features, palette='viridis')
    
    # Format feature names
    plt.ylabel('')
    cleaned_labels = [item.get_text().replace('_', ' ').title() for item in plt.gca().get_yticklabels()]
    plt.gca().set_yticklabels(cleaned_labels)
    
    # Set title
    plt.title(f'Top {n_top} Features in {group_name} Group', fontsize=16)
    plt.tight_layout()
    
    return plt.gcf(), None

# Main function to generate all visualizations
def generate_all_visualizations(data_path='../data/modeling_data.csv'):
    """Generate visualizations for all feature groups"""
    # Load data
    df = load_data(data_path)
    
    # Categorize columns
    categories = categorize_columns(df.columns)
    
    # Create a sample feature importance DataFrame (replace with your actual model results)
    # This simulates feature importance from a trained model
    feature_importance_data = []
    for group, features in categories.items():
        # Generate random importance scores (replace with actual model importance)
        for feature in features:
            importance = np.random.uniform(0, 1)
            feature_importance_data.append({
                'Feature': feature,
                'Importance': importance,
                'Group': group
            })
    
    feature_importance_df = pd.DataFrame(feature_importance_data)
    
    # Dictionary to store all visualizations
    visualizations = {}
    
    # Generate visualizations for each group
    for group_name, features in categories.items():
        if not features:  # Skip empty groups
            continue
            
        group_visualizations = {}
        
        # 1. Correlation heatmap for numeric features
        fig, error = plot_correlation_heatmap(df, features, group_name)
        if fig is not None:
            group_visualizations['correlation'] = fig
        
        # 2. Feature distributions for numeric features
        fig, error = plot_feature_distributions(df, features, group_name)
        if fig is not None:
            group_visualizations['distributions'] = fig
        
        # 3. Bar plots for categorical features
        fig, error = plot_categorical_features(df, features, group_name)
        if fig is not None:
            group_visualizations['categorical'] = fig
        
        # 4. Feature importance (if model is trained)
        fig, error = plot_feature_importance(feature_importance_df, group_name)
        if fig is not None:
            group_visualizations['importance'] = fig
        
        # Store all visualizations for this group
        if group_visualizations:
            visualizations[group_name] = group_visualizations
    
    return visualizations

# Execute the visualization generator
# In practice, you'd call this with your actual data path
visualizations = generate_all_visualizations('../data/modeling_data.csv')

# To display a specific visualization:
plt.figure(visualizations['Academic']['correlation'].number)
plt.show()

# Main execution code (uncomment to run)

if __name__ == "__main__":
    # Generate all visualizations
    visualizations = generate_all_visualizations()
    
    # Display or save all visualizations
    for group_name, group_viz in visualizations.items():
        for viz_type, fig in group_viz.items():
            plt.figure(fig.number)
            plt.show()
            # Alternatively, save to file:
            # fig.savefig(f"{group_name}_{viz_type}.png", dpi=300, bbox_inches='tight')
