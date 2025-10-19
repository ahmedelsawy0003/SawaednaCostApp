# migrate.ps1
# هذا الملف يقوم بإنشاء وتشغيل مهمة Cloud Run Job لتنفيذ ترحيلات قاعدة البيانات.

$DATABASE_URL = "postgresql://neondb_owner:npg_DXQFUvy2WK3a@ep-sparkling-poetry-adbaqr4r-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
$IMAGE_URL = "gcr.io/sawednaerp/sawaedna-app"
$REGION = "us-central1"
$JOB_NAME = "run-migrations"

Write-Host "================================================="
Write-Host "🚀 بدء تهيئة قاعدة البيانات (Migrations)"
Write-Host "================================================="

# 1. حذف أي Job قديم بنفس الاسم (لضمان البدء من جديد)
Write-Host "-> محاولة حذف أي مهمة سابقة..."
gcloud run jobs delete $JOB_NAME --region $REGION --quiet --format="none" 2>$null

# 2. إنشاء Job الجديد (في سطر واحد)
Write-Host "-> إنشاء مهمة Cloud Run Job: $JOB_NAME"
gcloud run jobs create $JOB_NAME `
    --image $IMAGE_URL `
    --command /bin/bash `
    --args "-c" `
    --args "flask db upgrade" `
    --set-env-vars DATABASE_URL=$DATABASE_URL `
    --region $REGION `
    --platform managed

# 3. تشغيل Job الجديد وانتظار اكتماله
Write-Host "-> تشغيل مهمة الترحيل والانتظار حتى النجاح..."
gcloud run jobs execute $JOB_NAME --wait

Write-Host "================================================="
Write-Host "✅ تم الانتهاء من عملية الترحيل"
Write-Host "================================================="