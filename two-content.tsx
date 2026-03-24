const layoutId = "two-content";
const layoutName = "Two Content";
const layoutDescription = "A slide with title and two side-by-side content areas";

const Schema = z.object({
  title: z.string().min(1).default("Slide Title"),
  left_title: z.string().default("Left Content"),
  left_image_url: z.string().url().default('/images/usdaw-template/logo.png').describe('Left column image URL'),
  left_image_file: z.string().optional().describe('Left column uploaded image'),
  left_content: z.string().default("Point one"),
  right_title: z.string().default("Right Content"),
  right_image_url: z.string().url().default('/images/usdaw-template/logo.png').describe('Right column image URL'),
  right_image_file: z.string().optional().describe('Right column uploaded image'),
  right_content: z.string().default("Point one")
});

const dynamicSlideLayout = ({ data }) => {
  const {
    title = 'Slide Title',
    left_title = 'Left Content',
    left_image_url,
    left_image_file,
    left_content = 'Point one',
    right_title = 'Right Content',
    right_image_url,
    right_image_file,
    right_content = 'Point one'
  } = data || {};

  const leftArray = Array.isArray(left_content) ? left_content : [left_content];
  const rightArray = Array.isArray(right_content) ? right_content : [right_content];

  // USDAW Corporate Colors
  const colors = {
    purple: '#8F1A95',
    darkBlueGray: '#44546A',
    lightGray: '#E7E6E6',
    white: '#FFFFFF'
  };

  // Container styles
  const containerStyle = {
    width: '100%',
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: colors.white,
    fontFamily: 'Calibri, sans-serif'
  };

  // Title area styles - Purple background with white text
  const titleAreaStyle = {
    backgroundColor: colors.purple,
    padding: '40px',
    marginBottom: '0'
  };

  const titleStyle = {
    fontSize: '32px',
    fontFamily: 'Calibri Light, Calibri, sans-serif',
    fontWeight: 'bold',
    color: colors.white,
    margin: '0',
    padding: '0'
  };

  // Content wrapper styles
  const contentWrapperStyle = {
    display: 'flex',
    flex: '1',
    overflow: 'hidden'
  };

  // Left column styles - Light gray background
  const leftColumnStyle = {
    flex: '1',
    backgroundColor: colors.lightGray,
    padding: '40px',
    overflowY: 'auto',
    borderRight: `3px solid ${colors.darkBlueGray}`
  };

  // Right column styles - White background
  const rightColumnStyle = {
    flex: '1',
    backgroundColor: colors.white,
    padding: '40px',
    overflowY: 'auto'
  };

  // Column title styles
  const columnTitleStyle = {
    fontSize: '18px',
    fontFamily: 'Calibri Light, Calibri, sans-serif',
    fontWeight: 'bold',
    color: colors.purple,
    marginTop: '0',
    marginBottom: '20px',
    paddingBottom: '10px',
    borderBottom: `2px solid ${colors.purple}`
  };

  // Image styles
  const imageStyle = {
    width: '100%',
    height: 'auto',
    maxHeight: '200px',
    objectFit: 'cover',
    marginBottom: '20px',
    borderRadius: '4px'
  };

  // List styles
  const listStyle = {
    listStyle: 'none',
    padding: '0',
    margin: '0'
  };

  const listItemStyle = {
    color: colors.darkBlueGray,
    fontSize: '14px',
    fontFamily: 'Calibri, sans-serif',
    marginBottom: '12px',
    lineHeight: '1.6'
  };

  return (
    <div style={containerStyle} data-layout="two-content">
      <div style={titleAreaStyle}>
        <h1 style={titleStyle}>{title}</h1>
      </div>
      <div style={contentWrapperStyle}>
        <div style={leftColumnStyle}>
          {(left_image_url || left_image_file) && (
            <img 
              src={left_image_file || left_image_url} 
              alt={left_title}
              style={imageStyle}
            />
          )}
          <h3 style={columnTitleStyle}>{left_title}</h3>
          <ul style={listStyle}>
            {leftArray.map((item, idx) => (
              <li key={idx} style={listItemStyle}>• {item}</li>
            ))}
          </ul>
        </div>
        <div style={rightColumnStyle}>
          {(right_image_url || right_image_file) && (
            <img 
              src={right_image_file || right_image_url} 
              alt={right_title}
              style={imageStyle}
            />
          )}
          <h3 style={columnTitleStyle}>{right_title}</h3>
          <ul style={listStyle}>
            {rightArray.map((item, idx) => (
              <li key={idx} style={listItemStyle}>• {item}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

