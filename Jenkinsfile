pipeline{
    agent any

    stages{
        stage('Cloning Repository') {
            steps{
                script{
                    echo 'Cloning the repository...'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'gittoken', url: 'https://github.com/Vbalimidi/MLOPS-hotel-reservation-predictor.git']])
                }
            }
        }
    }
}