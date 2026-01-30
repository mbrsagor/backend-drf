from drf_extra_fields.fields import Base64FileField


class CustomBase64FileField(Base64FileField):
    """
    Candidate class to allow file uploads (images + pdf + zip + mp4)
    via Base64.
    """
    ALLOWED_TYPES = ['pdf', 'zip', 'mp4', 'jpg', 'jpeg', 'png', 'gif', 'bin']

    def get_file_extension(self, filename, decoded_file):
        # 1. Try generic image detection
        try:
            extension = imghdr.what(filename, decoded_file)
            if extension:
                return "jpg" if extension == "jpeg" else extension
        except Exception:
            pass

        # 2. Check Magic Bytes for others
        # PDF: %PDF
        if decoded_file.startswith(b'%PDF'):
            return 'pdf'
        
        # ZIP: PK (also covers docx, xlsx, jar etc generic zip containers)
        if decoded_file.startswith(b'PK'):
            return 'zip'
            
        # MP4: ftyp in bytes 4-8 usually
        # Standard MP4/MOV header check
        if len(decoded_file) > 12:
            # Common ftyp markers
            if decoded_file[4:8] == b'ftyp':
                return 'mp4'

        # 3. Fallback: Try to use the header from the Base64 string if available
        # But Base64FileField structure separates decoding. 
        # If we can't detect, default to 'bin' or raise error.

        # Return generic 'bin' or raise? 
        # Better to return 'bin' to allow save, or specific extension if we trust the user.
        # But for now let's be safe.
        return 'bin'  # Default for unknown binary types

