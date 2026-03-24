const layoutId = "section-header";
const layoutName = "Section Header";
const layoutDescription = "Section divider with background image";

const Schema = z.object({
  title: z.string().default('Section Title'),
  subtitle: z.string().optional().describe('Optional subtitle'),
  overlay_opacity: z.number().default(0.6).describe('Overlay opacity 0-1')
});

const dynamicSlideLayout = ({ data }) => {
  const {
    title = 'Section Title',
    subtitle,
    overlay_opacity = 0.6
  } = data || {};

  const containerStyle = {
    width: '100%',
    height: '100vh',
    backgroundColor: '#8F1A95',
    backgroundImage: "url('/images/usdaw-template-new/background-2.png')",
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

  const contentStyle = {
    position: 'relative',
    zIndex: 2,
    textAlign: 'center'
  };

  const titleStyle = {
    fontSize: '56px',
    fontFamily: 'Calibri Light, sans-serif',
    fontWeight: '300',
    color: '#FFFFFF',
    margin: '0 0 15px 0'
  };

  const subtitleStyle = {
    fontSize: '24px',
    fontFamily: 'Calibri, sans-serif',
    color: '#FFFFFF',
    margin: 0,
    opacity: 0.85
  };

  return (
    <div style={containerStyle} data-layout="section-header">
      <div style={overlayStyle} />
      <div style={contentStyle}>
        <h1 style={titleStyle}>{title}</h1>
        {subtitle && (
          <p style={subtitleStyle}>{subtitle}</p>
        )}
      </div>
    </div>
  );
};

