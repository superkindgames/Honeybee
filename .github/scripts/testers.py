"""Sets up TestFlight testing via the App Store Connect API (run by .github/workflows/testers.yml).
- makes an internal "Family" group that gets every build automatically
- people already on the App Store Connect team: added to Family (Apple emails them the TestFlight invite)
- people not on the team yet: invited to the team as Developer (run again after they accept)
Emails come from the workflow input and are masked in the logs."""
import os, sys, time, json, jwt, requests

API = "https://api.appstoreconnect.apple.com/v1"
BUNDLE = "com.honeybeebaby.app"
key = os.environ["ASC_PRIVATE_KEY"]
if "BEGIN" not in key:
    key = "-----BEGIN PRIVATE KEY-----\n" + key.strip() + "\n-----END PRIVATE KEY-----\n"
tok = jwt.encode({"iss": os.environ["ASC_ISSUER_ID"], "iat": int(time.time()), "exp": int(time.time()) + 1100, "aud": "appstoreconnect-v1"},
                 key, algorithm="ES256", headers={"kid": os.environ["ASC_KEY_ID"], "typ": "JWT"})
H = {"Authorization": "Bearer " + tok, "Content-Type": "application/json"}

def call(method, path, body=None, ok=(200, 201, 204)):
    r = requests.request(method, API + path, headers=H, data=json.dumps(body) if body else None, timeout=60)
    if r.status_code not in ok:
        errs = "; ".join(e.get("detail") or e.get("title", "") for e in r.json().get("errors", [])) if r.content else ""
        raise RuntimeError(f"{method} {path.split('?')[0]} -> {r.status_code} {errs}")
    return r.json() if r.content else {}

people = []
raw = json.load(open(os.environ["GITHUB_EVENT_PATH"]))["inputs"]["testers"]
for item in raw.split(","):
    if "|" in item:
        email, name = item.split("|", 1)
        people.append((email.strip(), name.strip()))
if not people:
    sys.exit("No testers given.")

app = call("GET", f"/apps?filter[bundleId]={BUNDLE}")["data"]
if not app:
    sys.exit("App record not found in App Store Connect.")
app_id = app[0]["id"]
print("App found.")

groups = call("GET", f"/apps/{app_id}/betaGroups?limit=50")["data"]
fam = next((g for g in groups if g["attributes"]["name"] == "Family"), None)
if fam:
    gid = fam["id"]; print("Family group already exists.")
else:
    gid = call("POST", "/betaGroups", {"data": {"type": "betaGroups",
        "attributes": {"name": "Family", "isInternalGroup": True, "hasAccessToAllBuilds": True},
        "relationships": {"app": {"data": {"type": "apps", "id": app_id}}}}})["data"]["id"]
    print("Created the Family group (gets every new build automatically).")

for i, (email, name) in enumerate(people, 1):
    first, _, last = name.partition(" ")
    label = f"Person {i} ({first})"
    users = call("GET", f"/users?filter[username]={requests.utils.quote(email)}&limit=1")["data"]
    if not users:
        pending = call("GET", f"/userInvitations?filter[email]={requests.utils.quote(email)}&limit=1")["data"]
        if pending:
            print(f"{label}: team invite already sent; waiting for them to accept the email from Apple. Run this again after.")
            continue
        try:
            call("POST", "/userInvitations", {"data": {"type": "userInvitations", "attributes": {
                "email": email, "firstName": first or "Tester", "lastName": last or "Bee",
                "roles": ["DEVELOPER"], "allAppsVisible": True, "provisioningAllowed": False}}})
            print(f"{label}: not on the team yet -> team invite sent. After they accept it, run this again.")
        except RuntimeError as e:
            print(f"{label}: could not invite to the team: {e}")
        continue
    testers = call("GET", f"/betaTesters?filter[email]={requests.utils.quote(email)}&limit=1")["data"]
    try:
        if testers:
            call("POST", f"/betaGroups/{gid}/relationships/betaTesters", {"data": [{"type": "betaTesters", "id": testers[0]["id"]}]})
            tid = testers[0]["id"]
        else:
            tid = call("POST", "/betaTesters", {"data": {"type": "betaTesters",
                "attributes": {"email": email, "firstName": first or "Tester", "lastName": last or "Bee"},
                "relationships": {"betaGroups": {"data": [{"type": "betaGroups", "id": gid}]}}}})["data"]["id"]
        print(f"{label}: in the Family group.")
        try:
            call("POST", "/betaTesterInvitations", {"data": {"type": "betaTesterInvitations", "relationships": {
                "app": {"data": {"type": "apps", "id": app_id}}, "betaTester": {"data": {"type": "betaTesters", "id": tid}}}}})
            print(f"{label}: TestFlight invite email sent.")
        except RuntimeError as e:
            print(f"{label}: invite email not re-sent ({e}). They should already have it, or get it with the next build.")
    except RuntimeError as e:
        print(f"{label}: could not add to TestFlight: {e}")
