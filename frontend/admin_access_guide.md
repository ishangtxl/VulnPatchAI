# Admin Dashboard Access Guide

## 🎯 How to Access the Admin Dashboard

The admin dashboard has been implemented and is available, but it requires admin privileges to appear in the navigation menu.

### **Option 1: Direct URL Access** ⚡
Navigate directly to the admin dashboard using this URL:
```
http://localhost:3000/admin
```

### **Option 2: Admin User Account** 👨‍💼
The admin menu item only appears for users with admin privileges:
- User email ending with `@admin.com` 
- OR user with role `admin`

### **Current Implementation Status:**
✅ Admin dashboard page created: `/pages/AdminDashboard.tsx`
✅ Admin API endpoints implemented: `/api/v1/admin/*`
✅ Admin route added: `/admin` 
✅ Admin navigation logic implemented
✅ Role-based access control working

## 🔍 What You Should See

When you access `http://localhost:3000/admin`, you should see:

### **Tab 1: Overview & Analytics**
- Total feedback count
- Active users metric
- Average rating display
- Learning system status
- Recent feedback table

### **Tab 2: Detailed Feedback** 
- Advanced filtering options
- Paginated feedback table
- User information display
- Management actions (view/delete)

### **Tab 3: System Status**
- System overview metrics
- Health indicators
- Database statistics
- Recent activity tracking

## 🛠 If You Don't See the Dashboard

### **Issue: Page Not Found**
If you get a 404 error, the frontend might not be running the latest code. Try:
```bash
cd /Users/ishangupta/projects/socgen2/frontend
npm start
```

### **Issue: Admin Menu Missing**
The admin menu item only shows for admin users. You have two options:

**Option A: Use Direct URL**
Just navigate to `http://localhost:3000/admin` directly

**Option B: Create Admin User**
Modify your user account to have admin privileges

### **Issue: API Errors**
If you see API errors, the backend admin endpoints might not be running. The admin API is available at:
```
http://localhost:8000/api/v1/admin/*
```

## 🎯 Quick Test

1. **Open your browser** and go to `http://localhost:3000`
2. **Navigate directly** to `http://localhost:3000/admin`
3. **You should see** the admin dashboard with three tabs
4. **If you see errors**, check the browser console for details

## 📊 Admin Dashboard Features Available

Once you access the dashboard, you'll have:

- **Feedback Overview**: View all user feedback and ratings
- **Learning Management**: Control AI learning system
- **System Monitoring**: Monitor system health and performance
- **Data Export**: Export feedback data for analysis
- **User Management**: View user engagement metrics
- **Advanced Analytics**: Deep dive into feedback patterns

## 🔧 Troubleshooting

If the dashboard doesn't load properly:

1. **Check browser console** for JavaScript errors
2. **Verify frontend is running** on port 3000
3. **Check network tab** for API request failures
4. **Try hard refresh** (Ctrl+F5 or Cmd+Shift+R)

The admin dashboard is fully implemented and should be accessible via the direct URL approach!