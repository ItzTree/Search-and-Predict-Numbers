import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

DATA_DIR = 'data/'
PLOT_DIR = 'plots/'

'''
Args:
    target_day(int): The day you want to predict.
    data_dir(str): The directory where the group CSV files are stored.
Returns:
    pd.DataFrame: A DataFrame containing the combined data of relevent days.
                  Returns an empty DataFrame if no data is found.
    list: A list of the group IDs that were used for analysis.
'''
def load_cyclical_data(target_day, data_dir):
    print(f"--- Step 1: Loading historical data for predicting Day {target_day} ---")

    # Choose relevant days. e.g., 1, 8, 15, ...
    cycle_day = (target_day - 1) % 7 + 1
    relevant_group_ids = [day for day in range(cycle_day, target_day, 7)]

    if not relevant_group_ids:
        print(f"Error: No past data available in the cycle for Day {target_day}")
        return pd.DataFrame(), []
    
    print(f"Relevant past data groups found: {relevant_group_ids}")

    # Read and concat relevant days into one dataframe
    df_list = []
    for group_id in relevant_group_ids:
        file_path = os.path.join(data_dir, f"{group_id}.csv")
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                if not df.empty:
                    df_list.append(df)
            except pd.errors.EmptyDataError:
                print(f"Warning: File '{file_path}' is empty and will be skipped")
        else:
            print(f"Warning: File '{file_path}' not found and will be skipped")
    
    if not df_list:
        return pd.DataFrame(), []
    
    combined_df = pd.concat(df_list, ignore_index=True)
    print(f"Successfully loaded a total of {len(combined_df)} numbers for analysis")
    return combined_df, relevant_group_ids


'''
Args:
    df(pd.DataFrame): The combined DataFrame containg all relevant historical data.
    target_day(int): The target day, used for titling plots and reports.
    plot_dir(str): The directory where generated plots will be saved.
Returns:
    pd.Series: A pandas Series containing the frequency of each last digit(0-9).
    pd.Series: A pandas Series containing the frequency of each hundreds-bucket.
'''
def perform_core_pattern_analysis(df, target_day, plot_dir):
    print("--- Step 2: Performing Core Pattern Analysis ---")

    # Overall Distribution (Histogram + KDE)
    plt.figure(figsize=(12, 7))
    sns.histplot(df['number'], kde=True, bins=50)
    plt.title(f"Overall Number Distribution(for Target Day {target_day})", fontsize=16)
    plt.xlabel("Number", fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    
    save_path_dist = os.path.join(plot_dir, f"distribution_day_{target_day}.png")
    plt.savefig(save_path_dist)
    plt.close()
    print(f"-> Overall distribution plot saved to: {save_path_dist}")

    # Hundreds-Bucket Frequency
    hundreds_bucket = df['number'] // 100
    bucket_counts = hundreds_bucket.value_counts().sort_index()
    x_labels = bucket_counts.index * 100

    plt.figure(figsize=(24, 8))
    sns.barplot(x=x_labels, y=bucket_counts.values, color="skyblue")
    plt.title(f"Frequency by Hundreds-Bucket (for Target Day {target_day})", fontsize=16)
    plt.xlabel("Hundreds Bucket", fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    plt.xticks(rotation=45, fontsize=8)
    plt.tight_layout()
    
    save_path_bucket = os.path.join(plot_dir, f"hundreds_bucket_day_{target_day}.png")
    plt.savefig(save_path_bucket)
    plt.close()
    print(f"-> Hundreds-bucket frequency plot saved to: {save_path_bucket}")

    # Last Digit Frequency
    last_digits = df['number'] % 10
    last_digit_freq = last_digits.value_counts().reindex(range(10), fill_value=0).sort_index()
    print("-> Last Digit Frequency Analysis:")
    print(last_digit_freq.to_string())

    return last_digit_freq, bucket_counts


'''
Args:
    df(pd.DataFrame): The combined DataFrame containing all relevant historical data.
    relevant_group_ids(list): A list of the past days used in the analysis.
    target_dat(int): The target day, used for titling the plot.
    plot_dir(str): The directory where the generated plot will be saved.
Returns:
    pd.Series: A pandas Series containing the median value for each historical day.
'''
def perform_trend_analysis(df, relevant_group_ids, target_day, plot_dir):
    print("--- Step 3: Performing Simple Trend Analysis ---")

    # Calculate the median for each past day in the cycle
    medians_over_time = df.groupby('group_id')['number'].median().reindex(relevant_group_ids)

    plt.figure(figsize=(10, 6))
    medians_over_time.plot(kind='line', marker='o', linestyle='-')
    plt.title(f"Trend of Median Number for Cycle (Predicting Day {target_day})", fontsize=16)
    plt.xlabel("Day Number", fontsize=12)
    plt.ylabel("Median Number", fontsize=12)
    plt.xticks(relevant_group_ids)
    plt.grid(True, linestyle='--', alpha=0.6)

    save_path_trend = os.path.join(plot_dir, f"trend_analysis_day_{target_day}.png")
    plt.savefig(save_path_trend)
    plt.close()
    print(f"-> Trend analysis plot saved to: {save_path_trend}")

    return medians_over_time


'''
Args:
    df(pd.DataFrame): The combined DataFrame, used to define the candidate number pool.
    bucket_counts(pd.Series): The frequency of each hundreds-bucket.
    last_digit_freq(pd.Series): The frequency of each last digit.
    medians_over_time(pd.Series): The trend data of median values.
Returns:
    list[dict]: A list of dictionaries, where each dictionary contains a
                recommended 'number' and its calculated 'score'.
                Returns an empty list if no recommendations can be made.
'''
def recommend_top_numbers(df, bucket_counts, last_digit_freq, medians_over_time):
    print("--- Step 4: Generating Top 5 Recommendations ---")

    # Define the candidate pool: Focus on the core 50% of the data (between Q1 and Q3)
    q1 = df['number'].quantile(0.25)
    q3 = df['number'].quantile(0.75)

    # Adjust candidate pool based on trend
    trend_shift = 0
    if len(medians_over_time) > 1:
        last_two = medians_over_time.dropna().tail(2)
        if len(last_two) == 2:
            trend_shift = last_two.iloc[1] - last_two.iloc[0]
    
    # Shift the core range slightly based on the recent trend
    candidate_min = int(q1 + trend_shift / 2)
    candidate_max = int(q3 + trend_shift / 2)
    print(f"-> Candidate numbers will be selected from the trend-adjusted range: {candidate_min} to {candidate_max}")

    # Score each candidate number
    hot_last_digits = last_digit_freq.nlargest(3).index
    recommendations = []

    for number in range(candidate_min, candidate_max + 1):
        score = 0

        # How frequent is its hundreds-bucket
        bucket = number // 100
        if bucket in bucket_counts.index:
            score += bucket_counts[bucket]
        
        # If it has a "hot" last digit
        if number % 10 in hot_last_digits:
            score += bucket_counts.mean()
        
        if score > 0:
            recommendations.append({'number': number, 'score': score})
    
    if not recommendations:
        print("Warning: Could not generate recommendations. The candidate pool might be empty.")
        return []
    
    # Sort by score and return the top 5
    top_5 = sorted(recommendations, key=lambda x: x['score'], reverse=True)[:5]
    print("-> Scoring complete")

    return top_5


'''
Args:
    df(pd.DataFrame): The combined DataFrame, used to calculated overall stats like median.
    last_digit_freq(pd.Series): The last digit frequency data from the core analysis.
    medians_over_time(pd.Series): The trend data from the trend analysis.
    recommendations(list[dict]): The list of top recommended numbers with their scores.
    target_day(int): The target day, used for the report title.
'''
def generate_summary_report(df, last_digit_freq, medians_over_time, recommendations, target_day):
    print('=' * 20 + " ANALYSIS SUMMARY REPORT " + '=' * 20)
    print(f"STRATEGY FOR PREDICTING DAY: {target_day}")

    # Hot Spots from distribution
    q1 = df['number'].quantile(0.25)
    q3 = df['number'].quantile(0.75)
    median = df['number'].median()
    print(f"1. Core Number Range (Hot Spot):")
    print(f"  - 50% of numbers fall between {q1:.0f} and {q3:.0f}")
    print(f"  - The median (central point) is {median:.0f}")
    print(f"  - Recommendation: Check 'distribution_day_{target_day}.png' for specific high-frequency peaks")

    # Hot Last Digits
    hot_last_digits = last_digit_freq.nlargest(3)
    print(f"2. Most Frequent Last Digits (Top 3):")
    for digit, count in hot_last_digits.items():
        print(f"  - Digit '{digit}' appeared {count} times")
    print(f"  - Recommendation: Prioritize numbers ending in {list(hot_last_digits.index)}")

    # Trend
    if len(medians_over_time) > 1:
        last_two_medians = medians_over_time.dropna().tail(2)
        if len(last_two_medians) == 2:
            trend_direction = "UPWARD" if last_two_medians.iloc[1] > last_two_medians.iloc[0] else "DOWNWARD"
            print(f"3. Recent Trend Analysis:")
            print(f"  - The median has show a rect {trend_direction} trend")
            print(f"  - Recommendation: Consider adjusting your target range slightly in the {trend_direction.lower()} direction from the last median ({last_two_medians.iloc[1]:.0f})")
    
    print(f"4. TOP 5 RECOMMENDED NUMBERS: ")
    if recommendations:
        for i, rec in enumerate(recommendations):
            print(f"  {i+1}. Number: {rec['number']} (Score: {rec['score']:.2f})")
    else:
        print("  - No recommendations could be generated.")

    print('=' * 70)


'''
Args:
    target_day(int): The day for which you want to generate a prediction strategy.
'''
def run_full_analysis(target_day):
    os.makedirs(PLOT_DIR, exist_ok=True)

    # Load data
    df, relevant_groups = load_cyclical_data(target_day, DATA_DIR)
    if df.empty:
        return
    
    # Perfome core and trend analysis
    last_digit_freq, bucket_counts = perform_core_pattern_analysis(df, target_day, PLOT_DIR)
    medians_over_time = perform_trend_analysis(df, relevant_groups, target_day, PLOT_DIR)
    recommendations = recommend_top_numbers(df, bucket_counts, last_digit_freq, medians_over_time)

    # Generate summary
    generate_summary_report(df, last_digit_freq, medians_over_time, recommendations, target_day)