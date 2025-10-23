{{/*
Expand the name of the chart.
*/}}
{{- define "elder.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "elder.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "elder.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "elder.labels" -}}
helm.sh/chart: {{ include "elder.chart" . }}
{{ include "elder.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "elder.selectorLabels" -}}
app.kubernetes.io/name: {{ include "elder.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "elder.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "elder.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
PostgreSQL URL
*/}}
{{- define "elder.databaseUrl" -}}
{{- if .Values.config.databaseUrl }}
{{- .Values.config.databaseUrl }}
{{- else if .Values.postgresql.enabled }}
{{- printf "postgresql://%s:%s@%s-postgresql:5432/%s" .Values.postgresql.auth.username .Values.postgresql.auth.password (include "elder.fullname" .) .Values.postgresql.auth.database }}
{{- else }}
{{- required "Either config.databaseUrl or postgresql.enabled must be set" .Values.config.databaseUrl }}
{{- end }}
{{- end }}

{{/*
Redis URL
*/}}
{{- define "elder.redisUrl" -}}
{{- if .Values.config.redisUrl }}
{{- .Values.config.redisUrl }}
{{- else if .Values.redis.enabled }}
{{- if .Values.redis.auth.enabled }}
{{- printf "redis://:%s@%s-redis-master:6379/0" .Values.redis.auth.password (include "elder.fullname" .) }}
{{- else }}
{{- printf "redis://%s-redis-master:6379/0" (include "elder.fullname" .) }}
{{- end }}
{{- else }}
{{- required "Either config.redisUrl or redis.enabled must be set" .Values.config.redisUrl }}
{{- end }}
{{- end }}
