const layoutId = "title-only";
const layoutName = "Title Only";
const layoutDescription = "A slide with only a title, leaving the rest for custom content";

const Schema = z.object({
  title: z.string().min(1).default("Slide Title")
});

const dynamicSlideLayout = ({ data }) => {
  const {
    title = 'Slide Title'
  } = data || {};

  const containerStyle = {
    width: '100%',
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: '#FFFFFF'
  };

  const headerStyle = {
    backgroundColor: '#8F1A95',
    padding: '40px',
    borderBottom: '3px solid #8F1A95'
  };

  const titleStyle = {
    fontSize: '48px',
    fontFamily: 'Calibri Light, Calibri, sans-serif',
    color: '#FFFFFF',
    margin: '0',
    fontWeight: '300',
    letterSpacing: '0.5px'
  };

  const contentAreaStyle = {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px',
    backgroundColor: '#FFFFFF'
  };

  const placeholderStyle = {
    color: '#A5A5A5',
    fontSize: '18px',
    fontFamily: 'Calibri, sans-serif',
    textAlign: 'center'
  };

  return (
    <div style={containerStyle} data-layout="title-only">
      <div style={headerStyle}>
        <h1 style={titleStyle}>{title}</h1>
      </div>
      <div style={contentAreaStyle}>
        <p style={placeholderStyle}>[Content area - add your own content]</p>
      </div>
    </div>
  );
};

