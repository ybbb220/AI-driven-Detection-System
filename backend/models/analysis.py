from utils.database import db


class AnalysisRecord(db.Model):
    __tablename__ = 'analysis_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    ai_probability = db.Column(db.Numeric(5, 4), nullable=False)
    human_probability = db.Column(db.Numeric(5, 4), nullable=False)
    sentence_analysis = db.Column(db.JSON, nullable=False)
    analysis_time = db.Column(db.Numeric(8, 3), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_text': self.original_text,
            'ai_probability': float(self.ai_probability),
            'human_probability': float(self.human_probability),
            'sentence_analysis': self.sentence_analysis,
            'analysis_time': float(self.analysis_time),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }