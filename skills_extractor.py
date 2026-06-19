import re
from urllib.parse import quote

# A detailed mapping of key Data Engineering skills to their direct tutorial links
# on GeeksforGeeks (GFG) and W3Schools. For items where direct links don't exist,
# we construct targeted search links to ensure the user always has a learning resource.
SKILL_MAP = {
    "SQL": {
        "display_name": "SQL",
        "w3schools": "https://www.w3schools.com/sql/",
        "geeksforgeeks": "https://www.geeksforgeeks.org/sql-tutorial/"
    },
    "Python": {
        "display_name": "Python",
        "w3schools": "https://www.w3schools.com/python/",
        "geeksforgeeks": "https://www.geeksforgeeks.org/python-programming-language/"
    },
    "Java": {
        "display_name": "Java",
        "w3schools": "https://www.w3schools.com/java/",
        "geeksforgeeks": "https://www.geeksforgeeks.org/java/"
    },
    "Scala": {
        "display_name": "Scala",
        "w3schools": "https://www.w3schools.com/scala/",
        "geeksforgeeks": "https://www.geeksforgeeks.org/scala-programming-language/"
    },
    "R": {
        "display_name": "R",
        "w3schools": "https://www.w3schools.com/r/",
        "geeksforgeeks": "https://www.geeksforgeeks.org/r-tutorial/"
    },
    "Git": {
        "display_name": "Git",
        "w3schools": "https://www.w3schools.com/git/",
        "geeksforgeeks": "https://www.geeksforgeeks.org/git-tutorial/"
    },
    "MongoDB": {
        "display_name": "MongoDB",
        "w3schools": "https://www.w3schools.com/mongodb/",
        "geeksforgeeks": "https://www.geeksforgeeks.org/mongodb-tutorial/"
    },
    "PostgreSQL": {
        "display_name": "PostgreSQL",
        "w3schools": "https://www.w3schools.com/postgresql/",
        "geeksforgeeks": "https://www.geeksforgeeks.org/postgresql-tutorial/"
    },
    "MySQL": {
        "display_name": "MySQL",
        "w3schools": "https://www.w3schools.com/mysql/",
        "geeksforgeeks": "https://www.geeksforgeeks.org/mysql-tutorial/"
    },
    "Pandas": {
        "display_name": "Pandas",
        "w3schools": "https://www.w3schools.com/python/pandas/default.asp",
        "geeksforgeeks": "https://www.geeksforgeeks.org/pandas-tutorial/"
    },
    "NumPy": {
        "display_name": "NumPy",
        "w3schools": "https://www.w3schools.com/python/numpy/default.asp",
        "geeksforgeeks": "https://www.geeksforgeeks.org/numpy-tutorial/"
    },
    "AWS": {
        "display_name": "AWS (Amazon Web Services)",
        "w3schools": "https://www.w3schools.com/aws/",
        "geeksforgeeks": "https://www.geeksforgeeks.org/aws-tutorial/"
    },
    "GCP": {
        "display_name": "GCP (Google Cloud)",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+google+cloud",
        "geeksforgeeks": "https://www.geeksforgeeks.org/google-cloud-platform-gcp-tutorial/"
    },
    "Azure": {
        "display_name": "Microsoft Azure",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+azure",
        "geeksforgeeks": "https://www.geeksforgeeks.org/microsoft-azure-tutorial/"
    },
    "Docker": {
        "display_name": "Docker",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+docker",
        "geeksforgeeks": "https://www.geeksforgeeks.org/docker-tutorial/"
    },
    "Kubernetes": {
        "display_name": "Kubernetes",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+kubernetes",
        "geeksforgeeks": "https://www.geeksforgeeks.org/kubernetes-tutorial/"
    },
    "Terraform": {
        "display_name": "Terraform",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+terraform",
        "geeksforgeeks": "https://www.geeksforgeeks.org/terraform-tutorial/"
    },
    "Spark": {
        "display_name": "Apache Spark",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+apache+spark",
        "geeksforgeeks": "https://www.geeksforgeeks.org/apache-spark/"
    },
    "PySpark": {
        "display_name": "PySpark",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+pyspark",
        "geeksforgeeks": "https://www.geeksforgeeks.org/pyspark-tutorial/"
    },
    "Hadoop": {
        "display_name": "Hadoop",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+hadoop",
        "geeksforgeeks": "https://www.geeksforgeeks.org/hadoop-tutorial/"
    },
    "Airflow": {
        "display_name": "Apache Airflow",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+airflow",
        "geeksforgeeks": "https://www.geeksforgeeks.org/apache-airflow-tutorial/"
    },
    "dbt": {
        "display_name": "dbt (Data Build Tool)",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+dbt",
        "geeksforgeeks": "https://www.geeksforgeeks.org/introduction-to-dbt-data-build-tool/"
    },
    "Snowflake": {
        "display_name": "Snowflake",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+snowflake",
        "geeksforgeeks": "https://www.geeksforgeeks.org/snowflake-tutorial/"
    },
    "Kafka": {
        "display_name": "Apache Kafka",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+kafka",
        "geeksforgeeks": "https://www.geeksforgeeks.org/apache-kafka-tutorial/"
    },
    "Databricks": {
        "display_name": "Databricks",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+databricks",
        "geeksforgeeks": "https://www.geeksforgeeks.org/introduction-to-azure-databricks/"
    },
    "BigQuery": {
        "display_name": "BigQuery",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+bigquery",
        "geeksforgeeks": "https://www.geeksforgeeks.org/google-cloud-bigquery/"
    },
    "Redshift": {
        "display_name": "AWS Redshift",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+redshift",
        "geeksforgeeks": "https://www.geeksforgeeks.org/aws-redshift-data-warehouse/"
    },
    "Hive": {
        "display_name": "Apache Hive",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+hive",
        "geeksforgeeks": "https://www.geeksforgeeks.org/apache-hive-introduction/"
    },
    "Flink": {
        "display_name": "Apache Flink",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+flink",
        "geeksforgeeks": "https://www.geeksforgeeks.org/apache-flink-introduction/"
    },
    "ETL": {
        "display_name": "ETL Pipelines",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+etl",
        "geeksforgeeks": "https://www.geeksforgeeks.org/etl-extract-transform-and-load-process/"
    },
    "NoSQL": {
        "display_name": "NoSQL Databases",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+nosql",
        "geeksforgeeks": "https://www.geeksforgeeks.org/nosql-databases/"
    },
    "DSA": {
        "display_name": "DSA (Algorithms)",
        "w3schools": "https://www.w3schools.com/dsa/",
        "geeksforgeeks": "https://www.geeksforgeeks.org/data-structures/"
    },
    "Linux": {
        "display_name": "Linux / Bash",
        "w3schools": "https://www.w3schools.com/cybersecurity/cybersecurity_linux.php",
        "geeksforgeeks": "https://www.geeksforgeeks.org/linux-tutorials/"
    },
    "Bash": {
        "display_name": "Bash Shell scripting",
        "w3schools": "https://www.google.com/search?q=site:w3schools.com+bash",
        "geeksforgeeks": "https://www.geeksforgeeks.org/bash-scripting-introduction/"
    },
    "Excel": {
        "display_name": "Excel",
        "w3schools": "https://www.w3schools.com/excel/",
        "geeksforgeeks": "https://www.geeksforgeeks.org/excel-tutorials/"
    }
}

# Regex compiler with word boundary checks to avoid false positives (e.g. matching "Git" inside "Digital")
SKILL_PATTERNS = {}
for skill in SKILL_MAP.keys():
    # Escaping is important if skill name has symbols like C++
    escaped_skill = re.escape(skill)
    # Special cases:
    if skill.lower() == 'git':
        # Don't match "digital" or "legitimate"
        SKILL_PATTERNS[skill] = re.compile(r'\b(git|github)\b', re.IGNORECASE)
    elif skill.lower() == 'r':
        # Don't match single 'r' in words, must be stand-alone or formatted like "R programming"
        SKILL_PATTERNS[skill] = re.compile(r'\b(r|r-programming)\b', re.IGNORECASE)
    else:
        SKILL_PATTERNS[skill] = re.compile(rf'\b{escaped_skill}\b', re.IGNORECASE)


def extract_skills_from_text(text):
    """
    Scans the given text and returns a list of matched skill dicts with GeeksforGeeks and W3Schools links.
    """
    if not text:
        return []
    
    extracted = []
    
    # Simple clean text to help scanning
    clean_text = re.sub(r'[^\w\s\+#\-]', ' ', text)
    
    for skill_key, pattern in SKILL_PATTERNS.items():
        if pattern.search(clean_text) or pattern.search(text):
            info = SKILL_MAP[skill_key]
            extracted.append({
                "key": skill_key,
                "display_name": info["display_name"],
                "w3schools": info["w3schools"],
                "geeksforgeeks": info["geeksforgeeks"]
            })
            
    return extracted
