from supabase import create_client
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)
