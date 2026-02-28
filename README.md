# 🎬 IMDB Top 1000 Movies Interactive Dashboard

A professional Dash-based interactive dashboard for exploring and analyzing IMDB's highest-rated films.

## 📊 Quick Start

### Installation

```bash
# Install required packages
pip install -r requirements.txt
```

### Running the Dashboard

```bash
# Start the application
python movie_dashboard.py
```

Then open your browser to: **http://127.0.0.1:8050/**

## ✨ Features

### Interactive Filters
- 🗓️ **Year Range Slider**: Select movies from 1921-2020
- 🎭 **Genre Filter**: Choose from 24 movie genres
- ⭐ **Rating Threshold**: Filter by minimum IMDB rating (5.0-10.0)
- 🔄 **Reset Button**: Restore default view instantly

### Real-Time Metrics
- Total movies matching your filters
- Average IMDB rating
- Total user votes
- Total box office revenue

### 6 Professional Visualizations

1. **Rating vs Popularity** (Scatter Plot)
   - Shows correlation between movie quality and audience interest
   - Size represents runtime, color represents year

2. **Rating Distribution** (Histogram)
   - Understand the spread of ratings across the top 1000

3. **Rating Trends Over Time** (Line Chart)
   - Discover how movie quality has evolved across decades

4. **Top Genres** (Bar Chart)
   - Identify which genres dominate top-rated films

5. **Top Directors** (Bar Chart)
   - Find directors with consistently high-rated filmographies

6. **Rating vs Revenue** (Scatter Plot)
   - Explore relationship between critical acclaim and commercial success

## 📁 Project Files

- **movie_dashboard.py** - Main Dash application (550+ lines)
- **PROJECT_DOCUMENTATION.md** - Detailed technical documentation
- **requirements.txt** - Python dependencies
- **imdb_top_1000.csv** - Dataset (1,000 movies)
- **README.md** - This file

## 🔧 Technical Stack

| Component | Technology |
|-----------|-----------|
| Web Framework | Dash |
| Visualization | Plotly |
| Data Processing | Pandas, NumPy |
| Language | Python 3.x |

## 📈 Key Features Explained

### Multiple Callback System
The dashboard uses a sophisticated callback architecture that:
- Accepts 4 different inputs (year slider, genre dropdown, rating slider, reset button)
- Updates 13 different outputs simultaneously
- Filters data in real-time with zero page reloads
- Recalculates all metrics and visualizations instantly

### Data Preprocessing
Comprehensive data cleaning includes:
- Runtime parsing (text → integers)
- Revenue formatting (comma-separated → numeric)
- Genre extraction (string → list for filtering)
- Missing value handling (intelligent imputation)
- Feature engineering (decade extraction, rating categorization)

### Analytical Insights
The dashboard reveals:
- Strong correlation between ratings and popularity
- Survivorship bias in historical film data
- Genre diversity in critically-acclaimed cinema
- Variance in director consistency
- Disconnect between critical and commercial success

## 🎯 Target Users

- **Film Enthusiasts** - Discover highly-rated films in your favorite genres
- **Researchers** - Analyze cinema trends and director contributions
- **Students** - Learn interactive data visualization and analysis
- **Industry Professionals** - Benchmark movie performance metrics

## 💡 Example Questions You Can Answer

- What are the highest-rated Drama films from the 1990s?
- Which directors have the most consistent quality?
- How have movie ratings changed over time?
- Is there a relationship between ratings and box office success?
- What genres dominate the top 1000 films?

## 📊 Dataset Information

- **Source**: IMDB Top 1000 Movies
- **Records**: 1,000 films
- **Time Period**: 1921-2020
- **Fields**: 16 attributes per movie
- **Size**: ~1 MB

## 🚀 Performance

- **Load Time**: < 3 seconds
- **Filter Response**: < 1 second
- **Visualization Update**: Real-time
- **Memory Usage**: Minimal (in-memory dataset)

## 🎨 Design Highlights

- Clean, modern interface with professional color scheme
- Responsive layout works on desktop and tablet
- Clear visual hierarchy with meaningful sections
- Consistent typography and spacing
- Accessible font sizes and contrast ratios

## 📝 Code Quality

✅ Well-organized with clear section headers  
✅ Comprehensive docstrings for all functions  
✅ Inline comments explaining complex logic  
✅ Meaningful variable and function names  
✅ DRY principles throughout  
✅ Proper error handling for edge cases  

## 🔒 Security & Stability

- No external API calls (data self-contained)
- No user input injection risks
- Stable data types and error handling
- Works offline after initial load

## 📚 Documentation

See **PROJECT_DOCUMENTATION.md** for:
- Detailed technical architecture
- Data processing methodology
- Visualization rationale
- Key analytical insights
- Evaluation against requirements

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use a different port
python movie_dashboard.py --port 8051
```

### Missing Data Display
The dataset has complete information for ratings and titles, but box office revenue is missing for older films (pre-1990). This is expected and handled gracefully.

### Slow Performance
- Ensure you have Python 3.7+
- Check available RAM (recommend 2GB+)
- Close other applications

## 🔮 Future Enhancements

- [ ] Movie search functionality
- [ ] CSV export for filtered results
- [ ] Favorite filters saved locally
- [ ] Side-by-side director comparison
- [ ] Advanced statistical analysis
- [ ] Mobile app version
- [ ] Cloud deployment (AWS/Heroku)

## 📄 License

Educational Project - Final Exam  
Created: February 2026

## 👤 Author

Created as part of Data Analytics Coursework

---

**Enjoy exploring cinema! 🍿**
