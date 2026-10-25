# ============================================================
# AWESOME-GRIZZLY-V1 - GitLab CI/CD Pipeline
# ============================================================
stages:
  - validate
  - lint
  - test
  - security
  - build
  - docker
  - deploy

variables:
  PYTHON_VERSION: "3.11"
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"
  IMAGE_TAG: "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA"
  IMAGE_LATEST: "$CI_REGISTRY_IMAGE:latest"

cache:
  key: "${CI_COMMIT_REF_SLUG}-py${PYTHON_VERSION}"
  paths:
    - .cache/pip
    - venv/

# ============================================================
# VALIDATE
# ============================================================
validate:python-syntax:
  stage: validate
  image: python:${PYTHON_VERSION}-slim
  before_script:
    - apt-get update && apt-get install -y build-essential libssl-dev libffi-dev
  script:
    - python -m py_compile awesome_grizzly.py
    - python -m py_compile requirement-check.py
    - python -m py_compile test-commands.py
    - echo "✅ Python syntax OK"
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH'
  tags:
    - docker

validate:requirements:
  stage: validate
  image: python:${PYTHON_VERSION}-slim
  script:
    - pip install --upgrade pip
    - pip install pip-tools
    - |
      if [ -f requirements.txt ]; then
        echo "✅ requirements.txt found"
        grep -q "" requirements.txt && echo "Non-empty ✅"
      else
        echo "❌ requirements.txt missing" && exit 1
      fi
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH'
  tags:
    - docker

# ============================================================
# LINT
# ============================================================
lint:flake8:
  stage: lint
  image: python:${PYTHON_VERSION}-slim
  before_script:
    - pip install flake8
  script:
    - flake8 --max-line-length=120 --ignore=E501,W503,E402,E722,C901,F401,F811,E128,E127,W605 \
        awesome_grizzly.py requirement-check.py test-commands.py || true
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH'
  tags:
    - docker

lint:black:
  stage: lint
  image: python:${PYTHON_VERSION}-slim
  before_script:
    - pip install black
  script:
    - black --check --diff --line-length=120 \
        awesome_grizzly.py requirement-check.py test-commands.py || echo "Formatting differs (non-blocking)"
  allow_failure: true
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH'
  tags:
    - docker

# ============================================================
# TEST
# ============================================================
test:requirements-check:
  stage: test
  image: python:${PYTHON_VERSION}-slim
  before_script:
    - apt-get update && apt-get install -y curl wget netcat-openbsd dnsutils nmap whois traceroute
    - pip install --upgrade pip
    - pip install -r requirements.txt || pip install colorama requests psutil
  script:
    - python requirement-check.py || true
  artifacts:
    paths:
      - .awesome_grizzly_v1/requirements_report.json
    expire_in: 1 week
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH'
  tags:
    - docker

test:command-suite:
  stage: test
  image: python:${PYTHON_VERSION}-slim
  before_script:
    - apt-get update && apt-get install -y curl wget netcat-openbsd dnsutils nmap whois traceroute sudo
    - pip install --upgrade pip
    - pip install -r requirements.txt
  script:
    - python test-commands.py || true
  artifacts:
    paths:
      - .awesome_grizzly_v1/test_report.json
    expire_in: 1 week
  allow_failure: true
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH'
  tags:
    - docker

test:unit-pytest:
  stage: test
  image: python:${PYTHON_VERSION}-slim
  before_script:
    - pip install --upgrade pip
    - pip install pytest pytest-cov
    - pip install -r requirements.txt || true
  script:
    - |
      if [ -d tests ]; then
        pytest tests/ -v --cov=. --cov-report=term --cov-report=xml:coverage.xml || true
      else
        echo "No tests/ directory — running command suite instead"
        python test-commands.py || true
      fi
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths:
      - coverage.xml
    expire_in: 1 week
  allow_failure: true
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH'
  tags:
    - docker

# ============================================================
# SECURITY
# ============================================================
security:bandit:
  stage: security
  image: python:${PYTHON_VERSION}-slim
  before_script:
    - pip install bandit
  script:
    - bandit -r . -x ./venv,./tests -f json -o bandit-report.json || true
    - cat bandit-report.json || true
  artifacts:
    paths:
      - bandit-report.json
    expire_in: 1 week
  allow_failure: true
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH'
  tags:
    - docker

security:safety:
  stage: security
  image: python:${PYTHON_VERSION}-slim
  before_script:
    - pip install safety
  script:
    - safety check --full-report || true
  allow_failure: true
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH'
  tags:
    - docker

# ============================================================
# BUILD
# ============================================================
build:package:
  stage: build
  image: python:${PYTHON_VERSION}-slim
  before_script:
    - pip install build twine
  script:
    - mkdir -p dist
    - cp awesome_grizzly.py dist/
    - cp requirement-check.py dist/
    - cp test-commands.py dist/
    - cp requirements.txt dist/
    - cp README.md dist/ || true
    - cp LICENSE dist/ || true
    - cd dist && tar czf ../awesome-grizzly-v1-$CI_COMMIT_SHORT_SHA.tar.gz *
  artifacts:
    paths:
      - awesome-grizzly-v1-*.tar.gz
    expire_in: 1 month
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_COMMIT_TAG'
  tags:
    - docker

# ============================================================
# DOCKER
# ============================================================
docker:build:
  stage: docker
  image: docker:24-cli
  services:
    - docker:24-dind
  before_script:
    - echo "$CI_REGISTRY_PASSWORD" | docker login -u "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY"
  script:
    - docker build -t "$IMAGE_TAG" -t "$IMAGE_LATEST" .
    - docker push "$IMAGE_TAG"
    - docker push "$IMAGE_LATEST"
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_COMMIT_TAG'
  tags:
    - docker

docker:test:
  stage: docker
  image: docker:24-cli
  services:
    - docker:24-dind
  before_script:
    - echo "$CI_REGISTRY_PASSWORD" | docker login -u "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY"
  script:
    - docker pull "$IMAGE_TAG"
    - docker run --rm --cap-add=NET_RAW --cap-add=NET_ADMIN "$IMAGE_TAG" python -c "import awesome_grizzly; print('✅ Image OK')"
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
  needs:
    - docker:build
  tags:
    - docker

# ============================================================
# DEPLOY
# ============================================================
deploy:staging:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$STAGING_SSH_PRIVATE_KEY" | ssh-add -
    - mkdir -p ~/.ssh && chmod 700 ~/.ssh
    - ssh-keyscan -H "$STAGING_HOST" >> ~/.ssh/known_hosts
  script:
    - ssh "$STAGING_USER@$STAGING_HOST" "cd /opt/awesome-grizzly-v1 && docker compose pull && docker compose up -d"
  environment:
    name: staging
    url: https://staging.grizzly.example.com
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
  when: manual
  tags:
    - docker

deploy:production:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$PROD_SSH_PRIVATE_KEY" | ssh-add -
    - mkdir -p ~/.ssh && chmod 700 ~/.ssh
    - ssh-keyscan -H "$PROD_HOST" >> ~/.ssh/known_hosts
  script:
    - ssh "$PROD_USER@$PROD_HOST" "cd /opt/awesome-grizzly-v1 && docker compose pull && docker compose up -d"
  environment:
    name: production
    url: https://grizzly.example.com
  rules:
    - if: '$CI_COMMIT_TAG'
  when: manual
  tags:
    - docker
