# dags/spark_pi.py
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from airflow.providers.cncf.kubernetes.sensors.spark_kubernetes import SparkKubernetesSensor
from datetime import datetime, timedelta

NAMESPACE = 'spark-ns' 

default_args = {
    'owner': 'mokhtar',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'spark_pi_example',
    default_args=default_args,
    schedule_interval=None, 
    description='Submit Spark Pi Job on Kubernetes'
)

# Define the Spark application spec
spark_app = {
    "apiVersion": "sparkoperator.k8s.io/v1beta2",
    "kind": "SparkApplication",
    "metadata": {
        "name": "spark-pi",
        "namespace": f"{NAMESPACE}"  # Updated namespace
    },
    "spec": {
        "type": "Scala",
        "mode": "cluster",
        "image": "gcr.io/spark-operator/spark:v3.1.1",
        "imagePullPolicy": "Always",
        "mainClass": "org.apache.spark.examples.SparkPi",
        "mainApplicationFile": "local:///opt/spark/examples/jars/spark-examples_2.12-3.1.1.jar",
        "sparkVersion": "3.1.1",
        "restartPolicy": {
            "type": "Never"
        },
        "driver": {
            "cores": 1,
            "coreLimit": "1200m",
            "memory": "1G",
            "serviceAccount": "spark",
            "labels": {
                "purpose": "spark-batch-job"
            }
        },
        "executor": {
            "cores": 1,
            "instances": 2,
            "memory": "1G",
            "labels": {
                "purpose": "spark-batch-job"
            }
        },
        "monitoring": {
            "exposeDriverMetrics": True,
            "exposeExecutorMetrics": True,
            "prometheus": {
                "jmxExporterJar": "/prometheus/jmx_prometheus_javaagent-0.11.0.jar",
                "port": 8090
            }
        }
    }
}

# Create Spark submit operator
submit_spark = SparkKubernetesOperator(
    task_id='submit_spark',
    application_file=spark_app,
    namespace=NAMESPACE,  # Updated namespace
    dag=dag
)

# Create Spark monitor operator
monitor_spark = SparkKubernetesSensor(
    task_id='monitor_spark',
    application_name="{{ task_instance.xcom_pull(task_ids='submit_spark')['metadata']['name'] }}",
    namespace=NAMESPACE,  # Updated namespace
    dag=dag
)

submit_spark >> monitor_spark
