
pipeline {
    agent any

    stages {
        stage('Kubernetes Connection Test') {
            steps {
                withCredentials([
                    string(credentialsId: 'k8s-token', variable: 'K8S_TOKEN'),
                    string(credentialsId: 'k8s-ca', variable: 'K8S_CA_B64')
                ]) {
                    sh '''
                        export KUBECONFIG="$WORKSPACE/jenkins-kubeconfig"
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

                        kubectl get pods
                        kubectl get deployments
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'rm -f "$WORKSPACE/jenkins-kubeconfig"'
        }
    }
}
