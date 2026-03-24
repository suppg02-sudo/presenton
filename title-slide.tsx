const layoutId = "title-slide";
const layoutName = "Title Slide";
const layoutDescription = "A professional USDAW title slide with corporate branding";

const Schema = z.object({
  title: z.string().default('Presentation Title'),
  subtitle: z.string().default('Subtitle'),
  logo_url: z.string().optional().describe('Logo image URL')
});

const dynamicSlideLayout = ({ data }) => {
  const {
    title = 'Slide Title',
    subtitle = 'Subtitle',
    logo_url
  } = data || {};

  const containerStyle = {
    width: '100%',
    height: '100vh',
    backgroundColor: '#8F1A95',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '40px',
    boxSizing: 'border-box',
    position: 'relative',
    overflow: 'hidden'
  };

  const contentStyle = {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '24px',
    textAlign: 'center',
    maxWidth: '90%',
    position: 'relative',
    zIndex: 2
  };

  const titleStyle = {
    fontSize: '72px',
    fontFamily: 'Calibri Light, Calibri, sans-serif',
    fontWeight: 'bold',
    color: '#FFFFFF',
    margin: '0',
    lineHeight: '1.2',
    letterSpacing: '-0.5px'
  };

  const subtitleStyle = {
    fontSize: '36px',
    fontFamily: 'Calibri, sans-serif',
    color: '#FFFFFF',
    margin: '0',
    lineHeight: '1.3',
    fontWeight: '400'
  };

  const logoStyle = {
    position: 'absolute',
    top: '20px',
    right: '20px',
    height: '60px',
    width: 'auto',
    opacity: '0.95',
    zIndex: 3
  };

  return (
    <div style={containerStyle} data-layout="title-slide">
      <div style={contentStyle}>
        <h1 style={titleStyle}>{title}</h1>
        <p style={subtitleStyle}>{subtitle}</p>
      </div>
      {logo_url && <img src={logo_url} alt="Logo" style={logoStyle} />}
    </div>
  );
};
