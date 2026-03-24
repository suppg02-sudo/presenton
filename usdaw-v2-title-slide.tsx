const layoutId = "title-slide";
const layoutName = "Title Slide";
const layoutDescription = "USDAW title slide with background image and logo";

const Schema = z.object({
  title: z.string().default('Presentation Title'),
  subtitle: z.string().default('Subtitle'),
  date: z.string().optional().describe('Presentation date'),
  overlay_opacity: z.number().default(0.5).describe('Overlay opacity 0-1')
});

const dynamicSlideLayout = ({ data }) => {
  const {
    title = 'Presentation Title',
    subtitle = 'Subtitle',
    date,
    overlay_opacity = 0.5
  } = data || {};

  const containerStyle = {
    width: '100%',
    height: '100vh',
    backgroundColor: '#8F1A95',
    backgroundImage: "url('/images/usdaw-template-new/background-1.jpg')",
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '60px',
    boxSizing: 'border-box',
    position: 'relative'
  };

  const overlayStyle = {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: `rgba(143, 26, 149, ${overlay_opacity})`,
    zIndex: 1
  };

  const logoStyle = {
    position: 'absolute',
    top: '30px',
    right: '40px',
    height: '50px',
    zIndex: 3
  };

  const contentStyle = {
    position: 'relative',
    zIndex: 2,
    textAlign: 'center',
    maxWidth: '85%'
  };

  const titleStyle = {
    fontSize: '64px',
    fontFamily: 'Calibri Light, sans-serif',
    fontWeight: '300',
    color: '#FFFFFF',
    margin: '0 0 20px 0',
    lineHeight: '1.2'
  };

  const subtitleStyle = {
    fontSize: '28px',
    fontFamily: 'Calibri, sans-serif',
    color: '#FFFFFF',
    margin: '0 0 30px 0',
    opacity: 0.9
  };

  const dateStyle = {
    fontSize: '18px',
    fontFamily: 'Calibri, sans-serif',
    color: '#FFFFFF',
    margin: 0,
    opacity: 0.7
  };

  return (
    <div style={containerStyle} data-layout="title-slide">
      <div style={overlayStyle} />
      <img 
        src="/images/usdaw-template-new/usdaw-logo-white.svg" 
        alt="USDAW" 
        style={logoStyle}
      />
      <div style={contentStyle}>
        <h1 style={titleStyle}>{title}</h1>
        {subtitle && (
          <p style={subtitleStyle}>{subtitle}</p>
        )}
        {date && (
          <p style={dateStyle}>{date}</p>
        )}
      </div>
    </div>
  );
};

