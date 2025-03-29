import os
import sys
from google import genai  # Import the Gemini library
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns


GEMINI_API_KEY = "AIPROXY_KEY"
def load_data(filename):
    """Load CSV data into a Pandas DataFrame."""
    try:
        # Attempt to load with ISO-8859-1 encoding, which is broad.
        df = pd.read_csv(filename, encoding='ISO-8859-1')
        print(f"Loaded dataset with {df.shape[0]} rows and {df.shape[1]} columns.")
        return df
    except UnicodeDecodeError:
        try:
            # If ISO-8859-1 fails, try UTF-8, a very common encoding.
            df = pd.read_csv(filename, encoding='UTF-8')
            print(f"Loaded dataset with {df.shape[0]} rows and {df.shape[1]} columns.")
            return df
        except Exception as e:
            # Handle any other exceptions during file loading.
            print(f"Error loading data: {e}")
            sys.exit(1)
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)



def analyze_data_gemini(df):
    """Perform general data analysis using Gemini."""
    prompt = f"""
    Perform a comprehensive data analysis on the following dataset.

    Dataset Description:
    {df.head().to_markdown(index=False)}

    Provide the following information in your response, formatted as markdown:

    1.  Dataset Overview:
        * Describe the dataset, including the number of rows and columns.
        * List the columns and their data types.
        * Identify the key variables and their potential significance.

    2.  Summary Statistics:
        * Calculate and interpret descriptive statistics for numerical columns (mean, median, min, max, std).
        * Provide counts and unique values for categorical columns.

    3.  Missing Values:
        * Identify columns with missing values and the percentage of missing data in each.
        * Suggest potential reasons for missing data and how it might impact analysis.

    4.  Correlations:
        * Calculate the correlation matrix for numerical columns.
        * Describe any strong positive or negative correlations.
        * Explain how correlations might inform further analysis or modeling.

    5.  Initial Insights:
        * Summarize the main findings from the analysis.
        * Suggest potential areas for further investigation or visualization.
    """
    return generate_gemini_response(prompt)



def generate_visualizations_gemini(df):
    """
    Generate descriptions of visualizations using Gemini, based on the dataframe.
    """
    prompt = f"""
    You are a data visualization expert. A user has provided a dataset, and you need to suggest relevant visualizations.

    Dataset Description:
    {df.head().to_markdown(index=False)}

    Column Information:
    {pd.DataFrame(df.dtypes).to_markdown()}

    Based on this data, suggest visualizations that would be helpful for understanding the data.  Provide your response in markdown format.

    For each visualization, provide the following:

    1.  Visualization Type: (e.g., scatter plot, bar chart, histogram)
    2.  Columns Used: List the specific columns from the dataframe that would be used.
    3.  Purpose: Explain what the visualization would show and what insights it could reveal.
    4.  Formatting Details: Describe any specific formatting or customization that would improve the visualization (e.g., color palettes, axes labels, chart titles).
    """
    return generate_gemini_response(prompt)


def generate_visualizations(df):
    """Generate enhanced visualizations."""
    # Correlation Heatmap
    plt.figure(figsize=(10, 6))
    sns.heatmap(df.corr(numeric_only=True), annot=True, cmap='coolwarm', fmt='.2f')
    plt.title("Feature Correlation Heatmap")
    plt.savefig("correlation_heatmap.png", dpi=300)
    plt.close()

    # Top Rated Books Distribution
    if 'average_rating' in df.columns:
        plt.figure(figsize=(8, 5))
        sns.histplot(df['average_rating'].dropna(), bins=20, kde=True, color='green')
        plt.title("Distribution of Average Ratings")
        plt.xlabel("Average Rating")
        plt.ylabel("Frequency")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.savefig("rating_distribution.png", dpi=300)
        plt.close()


def generate_gemini_response(prompt):
    """Sends a prompt to the Gemini API and returns the response."""
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    """
    api_key = GEMINI_API_KEY
    client = genai.Client(api_key=api_key)
    model = "gemini-2.0-flash"  # Use a model that is suitable for text generation

    contents = prompt
    response_text = ""
    try:
        response = client.models.generate_content(
            model=model,
            contents=contents
        )
        response_text = response.text
    except Exception as e:
        print(f"Error generating content with Gemini: {e}")
        response_text = f"Error: {e}"

    return response_text



def generate_report(filename, gemini_analysis, gemini_visualizations):
    """Create README.md with analysis results."""
    with open("README.md", "w") as f:
        f.write(f"# Automated Data Analysis Report\n\n")
        f.write(f"## Dataset: {filename}\n\n")
        f.write("### Gemini Analysis\n\n")
        f.write(gemini_analysis + "\n\n")
        f.write("### Gemini Visualization Suggestions\n\n")
        f.write(gemini_visualizations + "\n\n")



def main():
    if len(sys.argv) != 2:
        print("Usage: uv run autolysis.py <dataset.csv>")
        sys.exit(1)

    filename = sys.argv[1]
    df = load_data(filename)
    gemini_analysis = analyze_data_gemini(df)
    gemini_visualizations = generate_visualizations_gemini(df)
    generate_visualizations(df)
    generate_report(filename, gemini_analysis, gemini_visualizations)
    print("Analysis complete. Check README.md")



if __name__ == "__main__":
    main()
