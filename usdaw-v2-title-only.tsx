const layoutId = "title-only";
const layoutName = "Title Only";
const layoutDescription = "Minimal slide with centered title";

const Schema = z.object({
  title: z.string().default('Title'),
  subtitle: z.string().optional().describe('Optional subtitle'),
  background_image: z.enum(['background-1', 'background-2', 'none']).default('none').describe('Background image'),
  overlay_opacity: z.number().default(0.7).describe('Overlay opacity if background used')
});

const dynamicSlideLayout = ({ data }) => {
  const {
    title = 'Title',
    subtitle,
    background_image = 'none',
    overlay_opacity = 0.7
  } = data || {};

  const backgrounds = {
    'background-1': '/images/usdaw-template-new/background-1.jpg',
    'background-2': '/images/usdaw-template-new/background-2.png',
    'none': null
  };

  const bgImage = backgrounds[background_image];
  const hasBackground = bgImage !== null;

  const containerStyle = {
    width: '100%',
    height: '100vh',
    backgroundColor: '#8F1A95',
    backgroundImage: hasBackground ? `url('${bgImage}')` : 'none',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
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
    fontSize: '52px',
    fontFamily: 'Calibri Light, sans-serif',
    fontWeight: '300',
    color: '#FFFFFF',
    margin: '0 0 20px 0'
  };

  const subtitleStyle = {
    fontSize: '24px',
    fontFamily: 'Calibri, sans-serif',
    color: '#FFFFFF',
    margin: 0,
    opacity: 0.85
  };

  return (
    <div style={containerStyle} data-layout="title-only">
      {hasBackground && (
        <div style={overlayStyle} />
      )}
      <div style={contentStyle}>
        <h1 style={titleStyle}>{title}</h1>
        {subtitle && (
          <p style={subtitleStyle}>{subtitle}</p>
        )}
      </div>
    </div>
  );
};

