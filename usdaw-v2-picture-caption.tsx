const layoutId = "picture-with-caption";
const layoutName = "Picture with Caption";
const layoutDescription = "Large image with title and caption below";

const Schema = z.object({
  title: z.string().default('Image Title'),
  image_url: z.string().optional().describe('Image URL'),
  image_file: z.string().optional().describe('Uploaded image path'),
  use_default_image: z.boolean().default(true).describe('Use default image'),
  caption: z.string().optional().describe('Image caption/description'),
  show_logo: z.boolean().default(true).describe('Show USDAW logo')
});

const dynamicSlideLayout = ({ data }) => {
  const {
    title = 'Image Title',
    image_url,
    image_file,
    use_default_image = true,
    caption,
    show_logo = true
  } = data || {};

  const imageSrc = image_url || image_file || (use_default_image ? '/images/usdaw-template-new/background-1.jpg' : null);

  const containerStyle = {
    width: '100%',
    height: '100vh',
    backgroundColor: '#FFFFFF',
    display: 'flex',
    flexDirection: 'column',
    boxSizing: 'border-box'
  };

  const headerStyle = {
    backgroundColor: '#8F1A95',
    padding: '20px 40px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  };

  const titleStyle = {
    fontSize: '32px',
    fontFamily: 'Calibri Light, sans-serif',
    fontWeight: '300',
    color: '#FFFFFF',
    margin: 0
  };

  const logoStyle = {
    height: '35px'
  };

  const imageContainerStyle = {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '30px 60px'
  };

  const imageStyle = {
    maxWidth: '100%',
    maxHeight: '400px',
    objectFit: 'contain',
    borderRadius: '4px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
  };

  const captionStyle = {
    fontSize: '18px',
    fontFamily: 'Calibri, sans-serif',
    color: '#555555',
    marginTop: '20px',
    textAlign: 'center',
    maxWidth: '80%'
  };

  return (
    <div style={containerStyle} data-layout="picture-with-caption">
      <div style={headerStyle}>
        <h1 style={titleStyle}>{title}</h1>
        {show_logo && (
          <img 
            src="/images/usdaw-template-new/usdaw-logo-white.svg" 
            alt="USDAW" 
            style={logoStyle}
          />
        )}
      </div>
      <div style={imageContainerStyle}>
        {imageSrc && (
          <img 
            src={imageSrc} 
            alt={caption || title} 
            style={imageStyle}
          />
        )}
        {caption && (
          <p style={captionStyle}>{caption}</p>
        )}
      </div>
    </div>
  );
};

