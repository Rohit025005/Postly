import streamlit as st
import requests
import base64
import urllib.parse

st.set_page_config(page_title="Simple Social", layout="wide")

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None


def get_headers():
    """Get authorization headers with token"""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def login_page():
    st.title("🚀 Welcome to Simple Social")

    email = st.text_input("Email:")
    password = st.text_input("Password:", type="password")

    if email and password:
        col1, col2 = st.columns(2)

        # ---------- LOGIN ----------
        with col1:
            if st.button("Login", type="primary", use_container_width=True):
                login_data = {"username": email, "password": password}

                response = requests.post(
                    "http://localhost:8000/auth/jwt/login",
                    data=login_data
                )

                if response.status_code == 200:
                    token_data = response.json()
                    st.session_state.token = token_data["access_token"]

                    user_response = requests.get(
                        "http://localhost:8000/auth/me",
                        headers=get_headers()
                    )

                    if user_response.status_code == 200:
                        st.session_state.user = user_response.json()
                        st.rerun()
                    else:
                        st.error("Failed to get user info")
                else:
                    st.error("Invalid email or password")

        # ---------- SIGN UP ----------
        with col2:
            if st.button("Sign Up", type="secondary", use_container_width=True):
                signup_data = {"email": email, "password": password}

                response = requests.post(
                    "http://localhost:8000/auth/register",
                    json=signup_data
                )

                if response.status_code == 201:
                    st.success("Account created! Click Login now.")
                else:
                    # 🔥 SAFE ERROR HANDLING
                    if response.headers.get("content-type", "").startswith("application/json"):
                        error_detail = response.json().get("detail", "Registration failed")
                    else:
                        error_detail = response.text or "Registration failed"

                    st.error(f"Registration failed: {error_detail}")
    else:
        st.info("Enter your email and password above")


def upload_page():
    st.title("📸 Share Something")

    uploaded_file = st.file_uploader("Choose media", type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv', 'webm'])
    caption = st.text_area("Caption:", placeholder="What's on your mind?")

    # in frontend.py upload_page()
    if uploaded_file and st.button("Share", type="primary"):
        with st.spinner("Uploading..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {"caption": caption}
            try:
                response = requests.post("http://localhost:8000/upload", files=files, data=data, headers=get_headers(), timeout=20)
            except requests.RequestException as e:
                st.error(f"Network error while uploading: {e}")
                return

            # Safe JSON decode
            try:
                payload = response.json()
            except ValueError:
                payload = None

            if response.status_code == 200:
                st.success("Posted!")
                st.rerun()
            else:
                # prefer JSON 'detail' if present, else show raw text
                if payload and "detail" in payload:
                    st.error(f"upload failed: {payload['detail']}")
                else:
                    body = response.text.strip()
                    st.error(f"upload failed: {body or 'unknown error'}")



def encode_text_for_overlay(text):
    """Encode text for ImageKit overlay - base64 then URL encode"""
    if not text:
        return ""
    # Base64 encode the text
    base64_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
    # URL encode the result
    return urllib.parse.quote(base64_text)




def create_cloudinary_transformed_url(original_url: str, transformation: str = None):
    """
    Simple Cloudinary transformation inserter.
    If original_url already contains '/upload/', we inject the transformation after it.
    Example transformation: 'c_scale,w_400' or 'c_fill,w_400,h_300,q_auto'
    """
    if not original_url:
        return ""

    if "/upload/" in original_url:
        parts = original_url.split("/upload/")
        if len(parts) == 2:
            base, rest = parts
            if transformation:
                return f"{base}/upload/{transformation}/{rest}"
            return original_url

    # If URL is not a Cloudinary delivery URL, return it unchanged
    return original_url


def feed_page():
    st.title("🏠 Feed")

    response = requests.get("http://localhost:8000/feed", headers=get_headers())
    if response.status_code == 200:
        posts = response.json()["posts"]

        if not posts:
            st.info("No posts yet! Be the first to share something.")
            return

        for post in posts:
            st.markdown("---")

            # Header with user, date, and delete button (if owner)
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{post['email']}** • {post['created_at'][:10]}")
            with col2:
                if post.get('is_owner', False):
                    if st.button("🗑️", key=f"delete_{post['id']}", help="Delete post"):
                        # Delete the post
                        response = requests.delete(f"http://localhost:8000/posts/{post['id']}", headers=get_headers())
                        if response.status_code == 200:
                            st.success("Post deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete post!")

            # Uniform media display with caption overlay
            caption = post.get('caption', '')
            if post['file_type'] == 'image':
                uniform_url = post['url']
                st.image(uniform_url, width=300)
            else:
                # For videos: specify only height to maintain aspect ratio + caption overlay
                uniform_video_url = post['url']
                st.video(uniform_video_url, width=300)
                st.caption(caption)

            st.markdown("")  # Space between posts
    else:
        st.error("Failed to load feed")


# Main app logic
if st.session_state.user is None:
    login_page()
else:
    # Sidebar navigation
    st.sidebar.title(f"👋 Hi {st.session_state.user['email']}!")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.token = None
        st.rerun()

    st.sidebar.markdown("---")
    page = st.sidebar.radio("Navigate:", ["🏠 Feed", "📸 Upload"])

    if page == "🏠 Feed":
        feed_page()
    else:
        upload_page()