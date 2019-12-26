gcloud ai-platform local train \
--package-path trainer \
--module-name trainer.task \
--job-dir data \
-- \
--work-dir data \
--images-count 1000