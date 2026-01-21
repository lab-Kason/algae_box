# Multi-Tank & Multi-User Support

## Current Capabilities ✅

### Multiple Tanks Per User
- ✅ **Database supports unlimited tanks** - SQLite schema with proper relationships
- ✅ **Mobile app shows all tanks** - Home screen lists all tanks
- ✅ **Each tank independent** - Separate sensor data, collection events, recommendations
- ✅ **Delete functionality** - New DELETE /api/tanks/<id> endpoint added
- ✅ **Mobile app delete button** - Swipe or tap delete icon with confirmation dialog

### Backend Multi-Tank Features
```python
# Database cascade delete - deleting a tank removes all associated data
sensor_readings = relationship('SensorReading', cascade='all, delete-orphan')
collection_events = relationship('CollectionEvent', cascade='all, delete-orphan')
```

**API Endpoints:**
- `GET /api/tanks` - List all tanks
- `POST /api/tanks` - Create new tank
- `PUT /api/tanks/<id>` - Update tank
- `DELETE /api/tanks/<id>` - Delete tank (NEW!)
- `GET /api/sensors/current/<tank_id>` - Tank-specific sensor data
- `GET /api/recommendations/<tank_id>` - Tank-specific recommendations

### How It Works Now

**Scenario 1: Multiple tanks for testing different algae**
```
User creates:
- Tank 1: Spirulina (pH 9.5, 100L)
- Tank 2: Chlorella (pH 6.8, 50L)
- Tank 3: Dunaliella (pH 8.5, 75L)

Each tank:
✅ Has independent sensor readings
✅ Gets species-specific recommendations
✅ Can be monitored/controlled separately
✅ Can be deleted without affecting others
```

**Scenario 2: Commercial operation**
```
Farm with 20 tanks:
- 10 tanks: Spirulina (production)
- 5 tanks: Chlorella (production)
- 3 tanks: Nannochloropsis (experimental)
- 2 tanks: Haematococcus (experimental)

✅ All monitored through one Railway backend
✅ Mobile app scrolls through all tanks
✅ Each gets independent recommendations
```

## Current Limitations ⚠️

### No User Authentication
- ❌ **No user accounts** - everyone sees same tanks
- ❌ **No login system** - no passwords/usernames
- ❌ **No user ownership** - can't restrict who sees/deletes tanks
- ❌ **No permissions** - anyone with APK can delete any tank

**What this means:**
- Current setup: **Single user or trusted team**
- Public deployment: **Anyone can see/modify all tanks**
- Multi-tenant: **Not supported yet**

### Shared Global Database
```
Railway Backend (Shared)
├── Tank 1 (visible to everyone)
├── Tank 2 (visible to everyone)
├── Tank 3 (visible to everyone)
└── Tank N (visible to everyone)
```

## Future: Multi-User Support

### Option A: Add Authentication (Recommended for production)
```python
# Add user table
class User(Base):
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    created_at = Column(DateTime)
    
class Tank(Base):
    # Add user_id foreign key
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='tanks')
```

**Benefits:**
- Each user sees only their tanks
- Login required
- Secure multi-tenant operation
- Different users can have different permissions

**Implementation effort:** Medium
- Add Flask-Login or JWT authentication
- Add signup/login screens in mobile app
- Filter API queries by user_id
- Add password reset, etc.

### Option B: Keep Simple, Deploy Per-User (Current approach)
**Benefits:**
- No complex auth needed
- Simple to use
- Good for single farm/lab
- Easy to understand

**Limitations:**
- One Railway deployment = one user/team
- To serve multiple users, need multiple Railway deployments
- No collaboration features

## Recommendations

### For Your Use Case (Single User/Lab):
✅ **Current setup is PERFECT**
- You can have unlimited tanks
- Delete function works
- No need for authentication complexity
- Railway free tier handles it

### For Commercial/Multi-User:
📋 **Roadmap:**
1. **Phase 1 (now)**: Use current system, unlimited tanks per deployment
2. **Phase 2**: Add simple PIN/password for app access
3. **Phase 3**: Full user authentication with accounts
4. **Phase 4**: Team/organization features, roles, permissions

## Testing Multi-Tank Right Now

Try creating multiple tanks from your phone:

```
Tank 1: "Test Spirulina" - Spirulina, 100L
Tank 2: "Test Chlorella" - Chlorella, 50L
Tank 3: "Small Experiment" - Nannochloropsis, 20L
```

Each will:
- Show on home screen
- Have independent dashboards
- Get species-specific recommendations
- Can be deleted individually

The backend ALREADY supports this - no code changes needed!

## Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Multiple tanks | ✅ Working | Unlimited tanks supported |
| Delete tanks | ✅ Added | API + mobile app with confirmation |
| Species-specific | ✅ Working | Each tank tracks its algae type |
| Independent monitoring | ✅ Working | Separate sensor data per tank |
| User accounts | ❌ Not implemented | Not needed for single user |
| Multi-tenant | ❌ Not supported | Would need authentication |
| Team collaboration | ❌ Not supported | Future enhancement |

**Bottom line:** Your system supports multiple tanks perfectly. Just need to fix the simulation to use species-specific parameters (next task).
