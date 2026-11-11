
pipeline {
    agent any

    parameters {
        choice(
            name: 'TARGET_COLOR',
            choices: ['green', 'blue'],
            description: 'Choose the inactive version to deploy'
        )
    }

    environment {
        KUBECONFIG = "${WORKSPACE}/jenkins-kubeconfig"
    }

    stages {

        stage('Configure Kubernetes Access') {
            steps {
                withCredentials([
                    string(credentialsId: 'k8s-token', variable: 'K8S_TOKEN'),
                    string(credentialsId: 'k8s-ca', variable: 'K8S_CA_B64')
                ]) {
                    sh '''
                        umask 077

                        cat > "$KUBECONFIG" <<EOF
apiVersion: v1
kind: Config
clusters:
- name: minikube
  cluster:
    server: https://192.168.49.2:8443
    certificate-authority-data: ${K8S_CA_B64}
contexts:
- name: jenkins-context
  context:
    cluster: minikube
    user: jenkins-deployer
current-context: jenkins-context
users:
- name: jenkins-deployer
  user:
    token: ${K8S_TOKEN}
EOF

                        kubectl get deployments
                    '''
                }
            }
        }

        stage('Check Active Version') {
            steps {
                script {
                    def active = sh(
                        script: "kubectl get svc ai-news-service -o jsonpath='{.spec.selector.version}'",
                        returnStdout: true
                    ).trim()

                    echo "Currently active version: ${active}"

                    if (active == params.TARGET_COLOR) {
                        error("Choose the inactive version. ${active} is already active!")
                    }

                    env.TARGET_COLOR = params.TARGET_COLOR
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                    -t ai-news-${TARGET_COLOR}:${BUILD_NUMBER} \
                    -f docker/Dockerfile.${TARGET_COLOR} .
                '''
            }
        }

        stage('Import Image into Minikube') {
            steps {
                sh '''
                    docker save ai-news-${TARGET_COLOR}:${BUILD_NUMBER} \
                    | docker exec -i minikube ctr -n k8s.io images import -
                '''
            }
        }

        stage('Deploy and Verify') {
            steps {
                sh '''
                    set -e

                    kubectl set image \
                    deployment/ai-news-${TARGET_COLOR} \
                    ai-news=ai-news-${TARGET_COLOR}:${BUILD_NUMBER}

                    kubectl rollout status \
                    deployment/ai-news-${TARGET_COLOR} \
                    --timeout=180s

                    kubectl get pods -l app=ai-news,version=${TARGET_COLOR}
                '''
            }
        }

        stage('Switch Traffic') {
            steps {
                sh '''
                    set -e

                    kubectl patch service ai-news-service \
                    --type=merge \
                    -p "{\\"spec\\":{\\"selector\\":{\\"app\\":\\"ai-news\\",\\"version\\":\\"${TARGET_COLOR}\\"}}}"

                    kubectl get svc ai-news-service \
                    -o jsonpath='Active version: {.spec.selector.version}{"\\n"}'

                '''
            }
        }
    }

    post {
        always {
            sh 'rm -f "$KUBECONFIG"'
        }
    }
}
