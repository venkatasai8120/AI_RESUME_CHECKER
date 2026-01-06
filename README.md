AI Resume Checker & ATS Skill Gap Analyzer

Author: Venkata Sai Reddy Peddireddy
GitHub: https://github.com/venkatasai8120

Live Application: https://ai-resume-checker-xrzj.onrender.com

Project Overview

AI Resume Checker & ATS Skill Gap Analyzer is a full-stack web application that analyzes a candidate’s resume against a specific job description to calculate a match score, identify missing skills, evaluate ATS (Applicant Tracking System) compatibility, and provide actionable resume improvement suggestions.

The application helps job seekers understand how well their resume aligns with a role before applying and assists recruiters in identifying strong candidates faster through objective resume scoring.

Problem Statement

Job seekers apply to roles without knowing whether their resume matches the job description.

Applicant Tracking Systems (ATS) reject resumes due to missing keywords, skill mismatches, or formatting issues.

Candidates struggle to identify which skills are mandatory versus optional.

Recruiters spend significant time screening poorly matched resumes.

No unified platform exists that combines resume–JD matching, skill gap analysis, ATS scoring, and improvement guidance.

Target Users
Job Seekers (Primary Users)

Who they are

Graduate students applying for internships or full-time roles

Recent graduates struggling to get interview calls

Working professionals switching roles or industries

Problems faced

No feedback after applying

ATS rejections without explanation

Skill confusion and blind applications

Goals

Know match percentage before applying

Identify missing skills

Receive ATS-friendly resume feedback

Recruiters / Hiring Managers (Secondary Users)

Who they are

Corporate recruiters

HR teams

Startup hiring managers

Problems faced

High resume volume

Manual skill screening

Inconsistent resume formats

Goals

Faster screening

Objective resume scoring

Better candidate shortlists

User Flow

User opens the application

Uploads resume (PDF/DOCX)

Pastes job description

System extracts resume text

Skills are extracted from resume and JD

Match score is calculated

Missing skills are identified

ATS compatibility is evaluated

AI-style improvement suggestions are generated

Results are displayed in the UI

MVP Features
Resume Upload and Text Extraction

Upload resumes in PDF or DOCX format

Automatically extracts clean text for analysis

Job Description Input

Users paste job description text

Text is cleaned and normalized

Skill Extraction

Extracts technical and soft skills

Uses predefined skill taxonomy and phrase matching

Resume & Job Description Matching

Compares extracted skills

Calculates match percentage score

Skill Gap Analysis

Identifies missing skills required for the role

ATS Compatibility Detection

Evaluates keyword coverage and structure

Flags potential ATS issues

AI-Based Resume Improvement Suggestions

Generates actionable improvement tips

Suggests keyword placement and bullet rewrites

Does not overwrite user content

Out of Scope (MVP)

Job recommendations

Full resume auto-rewriting

Cover letter generation

User authentication

Recruiter dashboards and bulk uploads

System Architecture

The system follows a modular architecture separating frontend, backend APIs, and processing modules.

Frontend Layer

HTML, CSS, JavaScript

Resume upload and JD input

Results dashboard

Backend Layer

Python Flask APIs

Handles uploads, processing, and orchestration

Processing Modules

Resume Parser

Skill Extractor

Matching & Scoring Engine

ATS Analyzer

AI Suggestion Generator

AI & Matching Pipeline

Collect resume and job description

Extract resume text

Clean job description

Extract skills from both

Compute matched and missing skills

Calculate match score

Run ATS checks

Generate AI-style suggestions

Return structured JSON to frontend

API Endpoints

GET /roles – Returns available job roles

POST /upload_resume – Upload resume and extract text

POST /analyze_text – Role-based skill gap analysis

POST /match_jd – ATS-style match scoring

POST /ai_suggestions – Resume improvement suggestions

Deployment & Continuous Deployment

Hosted on Render

Connected to GitHub with continuous deployment

OS-independent file paths using pathlib

Relative API URLs for local and production compatibility

Key Engineering Challenges & Fixes

Fixed CORS issues using flask-cors

Resolved Windows vs Linux path failures using pathlib

Eliminated production 500 errors

Fixed PowerShell file upload issues using curl.exe

Corrected frontend-backend JSON mismatches

Served static assets explicitly via Flask

Cleaned Git repo using .gitignore

Tech Stack

Frontend: HTML, CSS, JavaScript

Backend: Python, Flask

Parsing: PDF & DOCX parsing libraries

Deployment: Render

Version Control: Git, GitHub

Future Enhancements

LLM-powered resume rewriting

Skill learning path recommendations

Visual score analytics

Resume analysis history

Multi-role comparison

Optional database persistence

Key Takeaways

This project demonstrates:

Full-stack web development

REST API design

Resume parsing and NLP-style processing

ATS-aware scoring logic

Frontend–backend integration

Production deployment debugging

CI/CD with GitHub and Render
