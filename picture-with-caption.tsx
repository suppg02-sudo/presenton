const layoutId = "picture-with-caption";
const layoutName = "Picture with Caption";
const layoutDescription = "A slide with title, image area, and caption";

const Schema = z.object({
  image_url: z.string().url().default('/images/usdaw-template/logo.png').describe('Image URL'),
  image_file: z.string().optional().describe('Uploaded image file path'),
  image_alt: z.string().default('Usdaw Corporate Logo').describe('Alt text for accessibility'),
  caption: z.string().default('Usdaw Corporate Branding').describe('Caption text'),
  use_placeholder: z.boolean().default(false).describe('Force use of USDAW logo placeholder')
});

const dynamicSlideLayout = ({ data }) => {
  const {
    image_url = '',
    image_file = '',
    image_alt = 'Image caption',
    caption = 'Picture caption describing the image content',
    use_placeholder = false
  } = data || {};

  // Determine which image source to use with fallback logic
  const getImageSource = () => {
    // If placeholder is explicitly requested, use USDAW logo
    if (use_placeholder) {
      return '/images/usdaw-template/logo.png';
    }
    // Prefer image_file (uploaded) over image_url
    if (image_file) {
      return image_file;
    }
    // Fall back to image_url
    if (image_url) {
      return image_url;
    }
    // Final fallback to USDAW logo placeholder
    return '/images/usdaw-template/logo.png';
  };

  const imageSource = getImageSource();
  const hasCustomImage = (image_file || image_url) && !use_placeholder;

  return (
    <div style={{
      width: '100%',
      height: '100vh',
      backgroundColor: '#FFFFFF',
      display: 'flex',
      flexDirection: 'column',
      fontFamily: 'Calibri, sans-serif'
    }} data-layout="picture-with-caption">
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px',
        gap: '20px'
      }}>
        <img 
          src={imageSource} 
          alt={image_alt}
          style={{
            width: '600px',
            height: '400px',
            objectFit: hasCustomImage ? 'cover' : 'contain',
            backgroundColor: '#FFFFFF',
            border: '2px solid #8F1A95',
            aspectRatio: '3/2'
          }} 
        />
      </div>
      <div style={{
        backgroundColor: '#8F1A95',
        padding: '20px 40px',
        textAlign: 'center'
      }}>
        <p style={{
          color: '#FFFFFF',
          fontSize: '16px',
          fontFamily: 'Calibri Light, sans-serif',
          margin: '0',
          fontWeight: '300'
        }}>{caption}</p>
      </div>
    </div>
  );
};

