const layoutId = "title-and-content";
const layoutName = "Title and Content";
const layoutDescription = "A slide with a title and content area for bullet points or text";

const Schema = z.object({
  title: z.string().min(1).default('Slide Title'),
  header_image_url: z.string().url().default('/images/usdaw-template/logo.png').describe('Optional header image URL'),
  header_image_file: z.string().optional().describe('Optional uploaded header image file'),
  header_image_height: z.number().default(120).describe('Header image height in pixels'),
  content: z.union([z.string(), z.array(z.string())]).default('Content point one')
});

const dynamicSlideLayout = ({ data }) => {
  const {
    title = 'Slide Title',
    header_image_url,
    header_image_file,
    header_image_height = 150,
    content = 'Content point one'
  } = data || {};

  const contentArray = Array.isArray(content) ? content : [content];

  const headerStyle = {
    backgroundColor: '#8F1A95',
    color: '#FFFFFF',
    padding: '40px',
    fontFamily: 'Calibri Light, Calibri, sans-serif',
    fontSize: '32px',
    fontWeight: 'normal',
    margin: '0',
    borderBottom: '3px solid #8F1A95'
  };

  const containerStyle = {
    width: '100%',
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: '#FFFFFF'
  };

  const contentContainerStyle = {
    flex: '1',
    display: 'flex',
    flexDirection: 'column',
    padding: '40px',
    backgroundColor: '#FFFFFF',
    overflowY: 'auto'
  };

  const bodyTextStyle = {
    color: '#44546A',
    fontFamily: 'Calibri, sans-serif',
    fontSize: '18px',
    lineHeight: '1.6',
    margin: '0'
  };

  const bulletListStyle = {
    listStyle: 'none',
    padding: '0',
    margin: '0'
  };

  const bulletItemStyle = {
    color: '#44546A',
    fontFamily: 'Calibri, sans-serif',
    fontSize: '18px',
    lineHeight: '1.6',
    marginBottom: '12px',
    display: 'flex',
    alignItems: 'flex-start',
    gap: '12px'
  };

  const bulletPointStyle = {
    color: '#8F1A95',
    fontWeight: 'bold',
    marginRight: '8px',
    flexShrink: 0
  };

  const headerImageContainerStyle = {
    width: '100%',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '20px 40px',
    backgroundColor: '#FFFFFF',
    borderBottom: '1px solid #E0E0E0'
  };

  const headerImageStyle = {
    maxWidth: '100%',
    height: `${header_image_height}px`,
    objectFit: 'contain',
    borderRadius: '4px'
  };

  const imageSource = header_image_url || header_image_file;

  return (
    <div style={containerStyle} data-layout="title-and-content">
      <h1 style={headerStyle}>{title}</h1>
      {imageSource && (
        <div style={headerImageContainerStyle}>
          <img
            src={imageSource}
            alt="Header"
            style={headerImageStyle}
          />
        </div>
      )}
      <div style={contentContainerStyle}>
        {typeof content === 'string' && !Array.isArray(content) ? (
          <div style={bodyTextStyle}>{content}</div>
        ) : (
          <ul style={bulletListStyle}>
            {contentArray.map((item, idx) => (
              <li key={idx} style={bulletItemStyle}>
                <span style={bulletPointStyle}>•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

