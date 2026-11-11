
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
            stage('Trivy Filesystem Scan') {
    steps {
        sh '''
            echo "Starting Trivy filesystem scan..."
            trivy fs --scanners vuln,secret,misconfig --exit-code 0 .
        '''
    }
}

        stage('SonarQube Code Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'

                    withSonarQubeEnv('SonarQube') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=ai-news-generator \
                            -Dsonar.projectName='AI News Generator' \
                            -Dsonar.sources=app \
                            -Dsonar.sourceEncoding=UTF-8
                        """
                    }
                }
            }
        }


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

        stage('Trivy Docker Image Scan') {
            steps {
                sh '''
                    echo "Starting Trivy Docker image scan..."
                    trivy image --scanners vuln --severity HIGH,CRITICAL --exit-code 0 ai-news-${TARGET_COLOR}:${BUILD_NUMBER}
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


        stage('OWASP ZAP Baseline Scan') {
            steps {
                sh '''
                    set -e

                    mkdir -p "$WORKSPACE/zap-reports"

                    echo "Starting application port-forward..."

                    kubectl port-forward --address 127.0.0.1 \
                    svc/ai-news-service 18081:80 \
                    > "$WORKSPACE/zap-port-forward.log" 2>&1 &

                    PF_PID=$!
                    trap 'kill $PF_PID 2>/dev/null || true' EXIT

                    echo "Waiting for application..."

                    READY=0
                    for i in $(seq 1 30); do
                        if curl -fsS http://127.0.0.1:18081/ > /dev/null; then
                            READY=1
                            break
                        fi
                        sleep 2
                    done

                    if [ "$READY" -ne 1 ]; then
                        cat "$WORKSPACE/zap-port-forward.log"
                        exit 1
                    fi

                    echo "Starting OWASP ZAP Baseline Scan..."

                    docker run --rm --network host \
                    -v "$WORKSPACE/zap-reports:/zap/wrk/:rw" \
                    ghcr.io/zaproxy/zaproxy:stable \
                    zap-baseline.py \
                    -t http://127.0.0.1:18081 \
                    -r zap-report.html -I
                '''
            }
        }
}

    post {

        always {
            archiveArtifacts artifacts: 'zap-reports/zap-report.html', allowEmptyArchive: true
            sh 'rm -f "$KUBECONFIG"'
        }
    }
}
