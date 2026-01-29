# 🏉 Rugby API Integration Guide

## API Endpoints Tersedia

Sistem Rugby Genius anda kini mempunyai endpoints berikut untuk data live:

### 1. Check API Status
```
GET /api/rugby/status
```
**Response:** Account info, subscription plan, requests quota

### 2. Get Countries
```
GET /api/rugby/countries
```
**Response:** Senarai negara yang ada dalam database rugby

### 3. Get Leagues
```
GET /api/rugby/leagues
GET /api/rugby/leagues?country=Australia
GET /api/rugby/leagues?season=2023
```
**Response:** Senarai liga dan piala rugby

### 4. Get Teams
```
GET /api/rugby/teams?league=3&season=2023
GET /api/rugby/teams?search=All+Blacks
```
**Parameters:**
- `league` - League ID (default: 3 = Super Rugby)
- `season` - Season year (default: 2023)
- `search` - Cari nama team

### 5. Get Team Details
```
GET /api/rugby/team/123
```
**Response:** Maklumat terperinci tentang team

### 6. Get Standings
```
GET /api/rugby/standings?league=3&season=2023
```
**Response:** Kedudukan liga semasa

### 7. Get Games/Matches
```
GET /api/rugby/games?league=3&season=2023
GET /api/rugby/games?team=123
GET /api/rugby/games?date=2024-01-15
```
**Response:** Jadual dan keputusan perlawanan

### 8. Get Team Statistics
```
GET /api/rugby/team-stats?team=123&league=3&season=2023
```
**Response:** Statistik team untuk musim tersebut

### 9. Head-to-Head
```
GET /api/rugby/h2h?team1=123&team2=456
```
**Response:** Sejarah pertemuan antara dua team

---

## Popular League IDs

| League | ID | Country |
|--------|-----|---------|
| Rugby World Cup | 1 | World |
| Super Rugby | 3 | Australia/NZ |
| Premiership | 4 | England |
| Top 14 | 5 | France |
| Six Nations | 6 | Europe |
| Pro14/URC | 7 | Multi-nation |

---

## Test URLs

Cuba buka di browser:
- http://127.0.0.1:5000/api/rugby/status
- http://127.0.0.1:5000/api/rugby/countries
- http://127.0.0.1:5000/api/rugby/leagues
- http://127.0.0.1:5000/api/rugby/standings?league=3&season=2023

---

## API Quota

- **Plan:** Free
- **Daily Limit:** 100 requests/day
- **Reset:** Every 24 hours (UTC)

**Tip:** Cache data yang jarang berubah (countries, leagues) untuk jimat quota!

---

## Files Berkaitan

| File | Purpose |
|------|---------|
| `api_config.py` | API key & configuration |
| `app.py` | Flask endpoints |
| `test_rugby_api.py` | Test script |

---

## Seterusnya

Untuk integrate data live ke UI:
1. Tambah dropdown untuk pilih league dari API
2. Paparkan live standings di sidebar
3. Tunjuk upcoming games
4. Auto-update team logos dari API
