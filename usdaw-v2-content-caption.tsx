const layoutId = "content-with-caption";
const layoutName = "Content with Caption";
const layoutDescription = "Image on left with content and caption on right";

const Schema = z.object({
  title: z.string().default('Slide Title'),
  image_url: z.string().optional().describe('Image URL'),
  image_file: z.string().optional().describe('Uploaded image path'),
  use_default_image: z.boolean().default(true).describe('Use USDAW logo as placeholder'),
  caption: z.string().optional().describe('Image caption'),
  content: z.array(z.string()).default([]).describe('Content bullet points'),
  show_logo: z.boolean().default(true).describe('Show USDAW logo in header')
});

const dynamicSlideLayout = ({ data }) => {
  const {
    title = 'Slide Title',
    image_url,
    image_file,
    use_default_image = true,
    caption,
    content = [],
    show_logo = true
  } = data || {};

  const imageSrc = image_url || image_file || (use_default_image ? '/images/usdaw-template-new/logo.png' : null);

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

  const contentStyle = {
    flex: 1,
    display: 'flex',
    padding: '30px 40px',
    gap: '30px'
  };

  const imageContainerStyle = {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center'
  };

  const imageStyle = {
    maxWidth: '100%',
    maxHeight: '350px',
    objectFit: 'contain'
  };

  const captionStyle = {
    fontSize: '14px',
    fontFamily: 'Calibri, sans-serif',
    color: '#666666',
    marginTop: '10px',
    fontStyle: 'italic'
  };

  const textContainerStyle = {
    flex: 1
  };

  const listStyle = {
    fontSize: '20px',
    fontFamily: 'Calibri, sans-serif',
    color: '#333333',
    lineHeight: '1.7',
    margin: 0,
    paddingLeft: '25px'
  };

  const listItemStyle = {
    marginBottom: '12px'
  };

  return (
    <div style={containerStyle} data-layout="content-with-caption">
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
      <div style={contentStyle}>
        <div style={imageContainerStyle}>
          {imageSrc && (
            <img 
              src={imageSrc} 
              alt={caption || 'Image'} 
              style={imageStyle}
            />
          )}
          {caption && (
            <p style={captionStyle}>{caption}</p>
          )}
        </div>
        <div style={textContainerStyle}>
          <ul style={listStyle}>
            {content.map((item, idx) => <li key={idx} style={listItemStyle}>{item}</li>)}
          </ul>
        </div>
      </div>
    </div>
  );
};

