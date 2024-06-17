Design Document:

Requirements:
1) How this batch dataflow job can be deployed as IAC? Assuming both input and output data are in gcs how we can run this job without internet connectivity / external access.
2) Scheduled on a daily basis on cloud composer.

Key compenents needed:
- Terraform
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







