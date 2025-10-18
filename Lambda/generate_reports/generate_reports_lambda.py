import json
import boto3
import pandas as pd
from io import StringIO, BytesIO
import os

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Read environment variables 
    S3_INPUT_BUCKET = os.environ['INPUT_BUCKET']
    S3_OUTPUT_BUCKET = os.environ['OUTPUT_BUCKET']
   

    # Read input file from S3 for Part 1
    response = s3_client.get_object(Bucket=S3_INPUT_BUCKET, Key='pr.data.0.Current')
    csv_data = response['Body'].read().decode('utf-8')
    bls_df = pd.read_csv(StringIO(csv_data), sep='\t')
   

    # Perform Pandas operations Part 1
    bls_df.columns = bls_df.columns.str.replace(' ', '')
    bls_df['series_id'] = bls_df['series_id'].str.strip()
    bls_df['period'] = bls_df['period'].str.strip()
    
    grouped_bls_df = (
    bls_df.groupby(['series_id', 'year'])['value']
      .sum()
      .reset_index()
    )

    best_year_df = (
    grouped_bls_df.loc[
        grouped_bls_df.groupby('series_id')['value'].idxmax()
    ]
    )

    # export DataFrame into a excel report Part1
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        best_year_df.to_excel(writer, index=False, sheet_name='best_year_by_series')

    excel_buffer.seek(0)

    # Upload Excel file to output S3 bucket Part1
    s3_client.put_object(
        Bucket=S3_OUTPUT_BUCKET,
        Key='R01_best_year_by_series_report.xlsx',
        Body=excel_buffer.getvalue(),
        ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    # Read input file from S3 for Part 2
    response = s3_client.get_object(Bucket=S3_INPUT_BUCKET, Key='population_data.json')
    content = response['Body'].read().decode('utf-8')
    population_data = json.loads(content)
    
   

    # Perform Pandas operations Part 2
    population_df = pd.DataFrame(population_data['data'])
    filtered_pop_df = population_df.loc[(population_df['Year']>=2013) & (population_df['Year']<=2018)]
    mean_population = filtered_pop_df['Population'].mean()
    print("Population Mean = ", mean_population)
    std_population = round(filtered_pop_df['Population'].std(),2)
    print("Population Standard Deviation = ",std_population)

    # Combine report from Part 1 and Part 2
    bls_df_filtered = bls_df.loc[(bls_df['series_id'] == 'PRS30006032') & (bls_df['period']== 'Q01')]
    df_joined = pd.merge(bls_df_filtered, population_df, left_on = 'year', right_on = 'Year', how = 'left')
    df_joined['Population'] = df_joined['Population'].astype('Int64')
    df_report = df_joined[['series_id','year','period','value','Population']]

    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df_report.to_excel(writer, index=False, sheet_name='population_by_year_series')

    excel_buffer.seek(0)

    # Upload Excel file to output S3 bucket Part2
    s3_client.put_object(
        Bucket=S3_OUTPUT_BUCKET,
        Key='R02_population_by_year_series_report.xlsx',
        Body=excel_buffer.getvalue(),
        ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f"Excel report generated and uploaded to s3://{S3_OUTPUT_BUCKET}/"
        })
    }
