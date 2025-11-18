## **IntegriLAB: A Research Integrity \& Collaboration Platform**

IntegriLAB is a web-based system designed to promote 
**transparency, reproducibility, and accountability** 
in scientific research.  
It provides a unified environment where researchers can register projects, 
collaborate with team members, and track all research artifacts with 
**secure version control and audit trails**.

This repository is a \textit{sanitized public version} of the IntegriLAB platform 
prepared for scientific dissemination.  
All sensitive configuration files, credentials, and institution-specific data 
have been removed.

---

## Key Features

- **Structured Onboarding**  
  Institutes, Principal Investigators (PIs), and project members can be 
  registered through a guided workflow.

- **Transparent Research Tracking**  
  Every version of documents, datasets, and analyses is securely logged, 
  making all changes fully traceable.

- **Integration With Research Tools**  
  IntegriLAB is designed to interface with tools such as Overleaf, GitHub, 
  DataLad, and LabTrace.

- **Role-Based Access Control (RBAC)**  
  Access is regulated through predefined roles:  
  \textit{Administrator, Principal Investigator, Member}.

- **Secure Architecture**  
  Django-based backend, encrypted communication, and AWS deployment 
  via Elastic Beanstalk.

---

 ## Technology Stack

| **Layer** | **Technologies** |
|---------------|------------------------|
| Frontend | Bootstrap, JavaScript |
| Backend | Django (Python) |
| Database | PostgreSQL |
| Deployment | AWS Elastic Beanstalk |
| Versioning \& CI | GitHub |

---

## Repository Contents

This public repository includes:

- Core Django project structure (cleaned)
- Sample configuration templates
- Minimal example workflows

It **excludes**:

- Credentials or API keys  
- Institution-specific data  
- User profiles or datasets  
- Deployment secrets or AWS configuration files  

---

## Local Installation
#### 1. Clone the Repository
```bash
git clone https://github.com/Rubaida001/integriLAB-app.git
cd integriLAB-public

#### 2. Install Dependencies
pip install -r requirements.txt


#### 3. Run Database Migrations
python manage.py migrate


#### 4. Start the Development Server
python manage.py runserver

## Notes on the Public Version
This repository is intended for **scientific review, demonstration, and reproducibility documentation**.
The complete production system including infrastructure configuration,
deployments, user data, and institutional settings—remains private.

For inquiries or to request extended access, please contact:
\texttt{rubaida.easmin@kcl.ac.uk}
