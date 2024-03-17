from flask import Flask, jsonify, request
from flask_cors import CORS
from intersection import run_intersection_model  # Assuming this is your model function
import numpy as np
from addition import add  # Import the add function from addition.py