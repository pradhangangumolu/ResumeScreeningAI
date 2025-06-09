from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)
CORS(app)  # ✅ Allow frontend to talk to backend

# Load CSV files once at startup for efficiency
people = pd.read_csv("C:/Users/pradhan/Downloads/RESUME SCREENING AND MATCHING/01_people.csv")
education = pd.read_csv("C:/Users/pradhan/Downloads/RESUME SCREENING AND MATCHING/03_education.csv")
experience = pd.read_csv("C:/Users/pradhan/Downloads/RESUME SCREENING AND MATCHING/04_experience.csv")
abilities = pd.read_csv("C:/Users/pradhan/Downloads/RESUME SCREENING AND MATCHING/02_abilities.csv")
skills = pd.read_csv("C:/Users/pradhan/Downloads/RESUME SCREENING AND MATCHING/06_skills.csv")
person_skills = pd.read_csv("C:/Users/pradhan/Downloads/RESUME SCREENING AND MATCHING/05_person_skills.csv")

# Load model once at startup
print("🔄 Loading SBERT model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Prepare merged resume data
def prepare_resume_data():
    abilities_grouped = abilities.groupby('person_id')['ability'].apply(
        lambda x: ' '.join(str(i) for i in x if pd.notnull(i))
    ).reset_index()

    education_grouped = education.groupby('person_id')['program'].apply(
        lambda x: ' '.join(str(i) for i in x if pd.notnull(i))
    ).reset_index()

    experience_grouped = experience.groupby('person_id')['title'].apply(
        lambda x: ' '.join(str(i) for i in x if pd.notnull(i))
    ).reset_index()

    skill_map = person_skills.merge(skills, on='skill')
    skills_grouped = skill_map.groupby('person_id')['skill'].apply(
        lambda x: ' '.join(str(i) for i in x if pd.notnull(i))
    ).reset_index()

    merged = people[['person_id', 'name']].merge(abilities_grouped, on='person_id', how='left') \
        .merge(education_grouped, on='person_id', how='left') \
        .merge(experience_grouped, on='person_id', how='left') \
        .merge(skills_grouped, on='person_id', how='left')

    merged = merged.fillna('')
    merged['resume_text'] = (
        merged['ability'] + ' ' + merged['program'] + ' ' +
        merged['title'] + ' ' + merged['skill']
    )
    return merged.head(50)

merged_resumes = prepare_resume_data()

@app.route('/match', methods=['POST'])
def match_resumes():
    data = request.get_json()
    job_description = data.get('job_description', '').strip()
    
    if not job_description:
        return jsonify({'error': 'Job description is required'}), 400

    # Optionally truncate resume text
    merged_resumes['resume_text'] = merged_resumes['resume_text'].apply(lambda x: x[:1000])

    # Encode
    resume_embs = model.encode(
        merged_resumes['resume_text'].tolist(),
        convert_to_tensor=True,
        batch_size=8,
        show_progress_bar=False
    )
    jd_emb = model.encode(job_description, convert_to_tensor=True)

    # Compute similarity scores
    scores = util.cos_sim(jd_emb, resume_embs).flatten().tolist()
    merged_resumes['score'] = scores

    top_matches = merged_resumes.sort_values(by='score', ascending=False).head(5)

    results = [{
        'person_id': row['person_id'],
        'name': row['name'],
        'score': row['score']
    } for _, row in top_matches.iterrows()]

    return jsonify({'matches': results})

if __name__ == "__main__":
    app.run(debug=True)
