Design Document:

Requirements:
1) How this batch dataflow job can be deployed as IAC? Assuming both input and output data are in gcs how we can run this job without internet connectivity / external access.
2) Scheduled on a daily basis on cloud composer.

Key components needed:
- Terraform
- Google cloud IAM roles
- Google Cloud VPC Network
- Google Cloud Storage
- Google Data Flow
- Google Cloud Composer

Archtecture:
- IAM Roles and Permissions:
Creation of IAM roles needed for accessing GCS, DataFlow, Composer, VPC.

- VPC Network:
Creation of private VPC to ensure no internet connectivity. Google cloud composer to be attched with this VPC.

- Dataflow Job:
Develop Dataflow job using Apache Beam and upload it to GCS.
Configure the Dataflow worker nodes needed to run within the private VPC created.

- Cloud Composer
Create and configure a Cloud Composer environment within the private VPC.
Create a DAG to schedule and run the Dataflow job daily.

Detailed Steps to follow for the above setup ask:

1) Create IAM Roles and Permissions:

```
resource "google_service_account" "dataflow_service_account" {
  account_id   = "dataflow-sa"
  display_name = "Dataflow Service Account"
}

resource "google_project_iam_member" "dataflow_iam" {
  project = var.project_id
  role    = "roles/dataflow.admin"
  member  = "serviceAccount:${google_service_account.dataflow_service_account.account_id}"
}

resource "google_project_iam_member" "dataflow_storage_iam" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.dataflow_service_account.account_id}"
}
```

2) Create private VPC:

```
resource "google_compute_network" "vpc_network" {
  name = "dataflow-vpc"
}

resource "google_compute_subnetwork" "private_subnet" {
  name          = "private-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = "us-central1"
  network       = google_compute_network.vpc_network.name
  private_ip_google_access = true
}
```

3) Create buckets:

```
resource "google_storage_bucket" "input_bucket" {
  name = "dataflow-input-bucket"
}

resource "google_storage_bucket" "output_bucket" {
  name = "dataflow-output-bucket"
}
```

4) Create DataFlow Job template:

```
resource "google_storage_bucket_object" "dataflow_template" {
  name   = "dataflow-template"
  bucket = google_storage_bucket.input_bucket.name
  source = "path/to/template/file"
}
```

5) Configure GC Composer:

```
resource "google_composer_environment" "composer_env" {
  name   = "composer-environment"
  region = "us-central1"
  config {
    node_count = 2
    software_config {
      image_version = "composer-2.0.0-airflow-2.1.2"
    }
    private_environment_config {
      enable_private_environment = true
      network_project_id = google_compute_network.vpc_network.name
    }
  }
}
```

6) Run Jenkins pipeline to deploy above TF resources.

7) Create and Upload DAG to Cloud Composer:

```
from airflow import DAG
from airflow.providers.google.cloud.operators.dataflow import DataflowTemplateOperator
from airflow.utils.dates import days_ago

default_args = {
    'start_date': days_ago(1),
}

with DAG(
    'daily_dataflow_job',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
) as dag:
    start_dataflow_job = DataflowTemplateOperator(
        task_id='start_dataflow_job',
        template='gs://dataflow-input-bucket/path/to/template/file',
        parameters={
            'input': 'gs://dataflow-input-bucket/input-file',
            'output': 'gs://dataflow-output-bucket/output-file',
        },
        location='us-central1',
        network='dataflow-vpc',
        subnetwork='regions/us-central1/subnetworks/private-subnet',
    )
```









