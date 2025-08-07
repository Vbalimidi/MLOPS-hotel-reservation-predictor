pipeline{
    agent any

    environment{
        VENV_DIR = 'venv'
    }

    stages{
        stage('Cloning Repository') {
            steps{
                script{
                    echo 'Cloning the repository...'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'gittoken', url: 'https://github.com/Vbalimidi/MLOPS-hotel-reservation-predictor.git']])
                }
            }
        }

        stage('Setting up virtual environment'){
            steps{
                script{
                    echo('Setting up virtual environment')
                    sh'''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }
    }
}