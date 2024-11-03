from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Default arguments to apply to all tasks in the DAG
default_args = {
    'owner': 'airflow',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    dag_id='example_python_operator_dag',
    default_args=default_args,
    description='A simple DAG using PythonOperator',
    schedule_interval=timedelta(days=1),  # Run daily
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    # Define a function to print the current date
    def print_date():
        print(f"Current date and time: {datetime.now()}")


    # Define tasks using PythonOperator
    print_date_task = PythonOperator(
        task_id='print_date_task',
        python_callable=print_date
    )