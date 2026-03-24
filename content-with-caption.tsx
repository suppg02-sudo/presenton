const layoutId = "content-with-caption";
const layoutName = "Content with Caption";
const layoutDescription = "A slide with title, content area, and caption text";

const Schema = z.object({
  image_url: z.string().url().default('/images/usdaw-template/logo.png').describe('Featured image URL'),
  image_file: z.string().optional().describe('Uploaded image file path'),
  image_alt: z.string().default('Usdaw Corporate Branding').describe('Alt text for image'),
  content: z.string().default('Featured content description'),
  caption: z.string().default('Usdaw Corporate Template'),
  show_caption_as_overlay: z.boolean().default(false).describe('Show caption as purple overlay on image')
});

const dynamicSlideLayout = ({ data }) => {
  const {
    image_url = '',
    image_file = '',
    image_alt = 'Featured image',
    content = '',
    caption = 'Caption text goes here',
    show_caption_as_overlay = false
  } = data || {};

  const hasImage = image_url || image_file;
  const imageSource = image_url || image_file;

  const containerStyle = {
    width: '100%',
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: '#FFFFFF',
    fontFamily: 'Calibri, sans-serif'
  };

  const contentAreaStyle = {
    flex: 1,
    backgroundColor: '#FFFFFF',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px',
    overflow: 'auto',
    flexDirection: hasImage ? 'row' : 'column'
  };

  const contentBoxStyle = {
    textAlign: 'center',
    width: hasImage ? '50%' : '100%',
    maxWidth: hasImage ? '400px' : '800px',
    paddingRight: hasImage ? '20px' : '0'
  };

  const imageContainerStyle = {
    position: 'relative',
    width: hasImage ? '50%' : '0',
    maxWidth: hasImage ? '500px' : '0',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    paddingLeft: hasImage ? '20px' : '0'
  };

  const imageStyle = {
    width: '100%',
    height: 'auto',
    maxHeight: '500px',
    objectFit: 'contain',
    borderRadius: '8px',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
  };

  const overlayStyle = show_caption_as_overlay && hasImage ? {
    position: 'absolute',
    bottom: '0',
    left: '0',
    right: '0',
    backgroundColor: 'rgba(143, 26, 149, 0.95)',
    color: '#FFFFFF',
    padding: '20px',
    fontFamily: 'Calibri Light, Calibri, sans-serif',
    fontSize: '14px',
    textAlign: 'center',
    borderRadius: '0 0 8px 8px'
  } : {};

  const contentDisplayStyle = {
    width: '100%',
    minHeight: hasImage ? '200px' : '300px',
    backgroundColor: '#F5F5F5',
    borderRadius: '8px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: '20px',
    padding: '20px',
    color: '#44546A',
    fontSize: '16px',
    fontFamily: 'Calibri, sans-serif',
    wordWrap: 'break-word',
    overflowWrap: 'break-word'
  };

  const captionBarStyle = {
    backgroundColor: '#8F1A95',
    color: '#FFFFFF',
    padding: '20px 40px',
    fontFamily: 'Calibri Light, Calibri, sans-serif',
    fontSize: '16px',
    fontWeight: 'normal',
    textAlign: 'center',
    borderTop: '3px solid #8F1A95'
  };

  return (
    <div style={containerStyle} data-layout="content-with-caption">
      <div style={contentAreaStyle}>
        {hasImage && (
          <div style={imageContainerStyle}>
            <div style={{ position: 'relative', width: '100%' }}>
              <img
                src={imageSource}
                alt={image_alt}
                style={imageStyle}
              />
              {show_caption_as_overlay && (
                <div style={overlayStyle}>
                  {caption}
                </div>
              )}
            </div>
          </div>
        )}
        <div style={contentBoxStyle}>
          <div style={contentDisplayStyle}>
            {content || '[Content Area]'}
          </div>
        </div>
      </div>
      {!show_caption_as_overlay && (
        <div style={captionBarStyle}>
          {caption}
        </div>
      )}
    </div>
  );
};

