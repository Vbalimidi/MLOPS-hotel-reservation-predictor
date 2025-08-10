pipeline{
    agent any

    environment{
        VENV_DIR = 'venv'
        GCP_PROJ ="rare-nectar-466710-v9"
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
    }

    stages{
        stage('Cloning Repository') {
            steps{
                script{
                    echo 'Cloning the repository....'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'gittoken', url: 'https://github.com/Vbalimidi/MLOPS-hotel-reservation-predictor.git']])
                }
            }
        }

        stage('Setting up virtual environment'){
            steps{
                script{
                    echo('Setting up virtual environment....')
                    sh'''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }

        stage('Building and pushing docker image to GCR'){
            steps{
                withCredentials([file(credentialsId : 'gcp-key', variable: 'Google-app-creds')]){
                    script{
                        echo 'Building and pushing docker image to GCR'
                        sh'''
                        export PATH=$PATH:$(GCLOUD_PATH)
                        gcloud auth activate-service-account --key-file=${Google-app-creds}
                        gcloud config set project ${GCP_PROJ}
                        gcloud auth configure-docker --quiet
                        docker build -t grc.io/${GCP_PROJ}/hotel-resevation .
                        docker push grc.io/${GCP_PROJ}/hotel-resevation
                        '''
                    }
                }
            }
        }
    }
}