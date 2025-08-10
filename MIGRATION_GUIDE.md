# 🚀 Migration Guide: SQLite to PostgreSQL on Render

This guide walks you through migrating your dream analytics data from SQLite to PostgreSQL on Render.com using CSV export/import.

## 📋 **Step 1: Export Data from SQLite**

**From your local machine where you have the SQLite database:**

1. **Find your database file** (one of these):
   - `dreams_complete.db`
   - `dreams.db` 
   - Any `.db` file with your dream data

2. **Run the export script**:
   ```bash
   python export_to_csv.py
   ```

3. **What this creates**:
   - `dreams_export.csv` file (estimated 10-50MB)
   - Contains all your dream data ready for PostgreSQL

**Expected output:**
```
🔄 Dreams Database CSV Exporter
========================================
📤 Exporting data from: dreams_complete.db
   Available tables: ['dreams', 'sqlite_sequence']
   Found dreams table
   Columns: ['id', 'original_id', 'username', 'age_at_dream', ...]
   Exported 1000 rows...
   Exported 50000 rows...
   Exported 115624 rows...
✅ Export complete!
   File: dreams_export.csv
   Size: 45.2 MB
   Rows: 115624
```

---

## 🌐 **Step 2: Deploy to Render**

1. **Connect Repository**: 
   - Go to [Render.com](https://render.com)
   - Connect the `clean-deploy` branch of your GitHub repo

2. **Render will automatically**:
   - Create PostgreSQL database (`dreemz-db`)
   - Deploy Flask application
   - Set `DATABASE_URL` environment variable

3. **Wait for deployment** to complete (usually 2-5 minutes)

---

## 📤 **Step 3: Upload CSV to Render**

**Option A: Using Render Shell**
1. Go to your service in Render dashboard
2. Click **"Shell"** tab
3. Upload `dreams_export.csv` using drag & drop or:
   ```bash
   # If you have the CSV on GitHub or accessible URL:
   curl -O https://your-csv-location/dreams_export.csv
   ```

**Option B: Using Git (if CSV is small enough)**
1. Add CSV to a temporary branch:
   ```bash
   git checkout -b temp-migration
   git add dreams_export.csv
   git commit -m "Temporary: Add CSV for migration"
   git push origin temp-migration
   ```
2. Deploy this branch temporarily, then switch back

---

## 💾 **Step 4: Import Data to PostgreSQL**

**In Render Shell:**

```bash
python import_from_csv.py
```

**Expected output:**
```
🔄 Dreams Database CSV Importer
📥 Importing CSV data to PostgreSQL...
========================================
✅ Connected to PostgreSQL
1. Creating table structure...
   ✅ Table created
2. Importing CSV data...
   CSV headers: ['original_id', 'username', 'age_at_dream', ...]
   Imported 1000 rows...
   Imported 50000 rows...
   Imported 115624 rows...
   ✅ Imported 115624 rows
3. Creating indexes...
   ✅ Indexes created
4. ✅ All changes committed

🎉 Import successful!
   Total dreams: 115,624
   Unique titles: 36,381
   Categories: 30

📊 Top dreams:
   'become soccer player': 4737 dreams
   'become rich': 3906 dreams
   'earn money': 1866 dreams
```

---

## ✅ **Step 5: Verify Deployment**

1. **Visit your Render URL**
2. **Test the dashboard**:
   - Categories Analysis should show ~30 categories
   - Unique Dreams should show ~36K titles
   - Age filtering should work

3. **Check API endpoints**:
   - `https://your-app.onrender.com/api/status`
   - `https://your-app.onrender.com/api/categories-analysis`

---

## 🧹 **Step 6: Cleanup**

1. **Remove CSV file** from Render:
   ```bash
   rm dreams_export.csv
   ```

2. **Delete temporary Git branch** (if used):
   ```bash
   git branch -D temp-migration
   git push origin --delete temp-migration
   ```

---

## 🔧 **Troubleshooting**

### **Export Issues**
- **Database not found**: Make sure you're in the directory with your `.db` file
- **Permission errors**: Check file permissions on database file
- **Empty export**: Verify your database has a `dreams` table

### **Import Issues**
- **DATABASE_URL not found**: Make sure PostgreSQL add-on is enabled in Render
- **CSV not found**: Ensure `dreams_export.csv` is in the current directory
- **Connection errors**: Wait a few minutes for PostgreSQL to fully initialize

### **Dashboard Issues**  
- **No data showing**: Check browser console for API errors
- **500 errors**: Check Render logs for Python errors
- **Empty categories**: Verify data was imported correctly

---

## 📊 **Expected Results**

After successful migration, your dashboard should show:

- **Total Dreams**: ~115,624
- **Unique Titles**: ~36,381  
- **Categories**: ~30 categories
- **Subcategories**: ~245 subcategories
- **Top Categories**: Career & Professional, Money & Wealth, Sports & Athletics

---

## 🆘 **Need Help?**

If you encounter issues:

1. **Check Render logs** in the dashboard
2. **Verify CSV file** was exported correctly
3. **Test database connection** in Render shell:
   ```bash
   python -c "import psycopg2; print('PostgreSQL OK')"
   ```
4. **Re-run import** if needed (script handles existing data)

**Your dream analytics dashboard will be live and ready! 🎉**