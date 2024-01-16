### Get Started
1. settings에 API_MODELS에 models 모듈 설정
2. settings에 API_MODELS_D_TS에 ts파일 경로 설정
3. settings의 INSTALLED_APPS에 'backend_core' 추가
4. urls.py에 path('api/', include('backend_core.urls')), 추가

### TODO
1. API_MODELS 설정은 list 타입으로 변환
2. get 쿼리는 cnpg-ro 로 요청 / 나머지는 cnpg-rw 로 분리 요청 처리
3. 검색기능 